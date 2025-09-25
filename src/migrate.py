from pymilvus import Collection, connections, FieldSchema, CollectionSchema, DataType
import time
import json
import os # Import os để kiểm tra/tạo thư mục

# --- 1. Thông tin kết nối Milvus cục bộ ---
LOCAL_MILVUS_HOST = "localhost"
LOCAL_MILVUS_PORT = "19530"

# --- 2. Thông tin kết nối Zilliz Cloud ---
# Thay thế bằng thông tin thực tế của bạn từ Zilliz Cloud
ZILLIZ_CLOUD_ENDPOINT = os.getenv("ZILLIZ_CLOUD_ENDPOINT")
ZILLIZ_CLOUD_API_KEY = os.getenv("ZILLIZ_CLOUD_API_KEY") 

# --- 3. Cấu hình di chuyển dữ liệu ---
COLLECTION_NAME_TO_MIGRATE = "recipes" # Tên của Collection bạn muốn di chuyển

# Batch size cho việc đọc và chèn dữ liệu
# Điều chỉnh tùy theo kích thước vector và RAM của bạn
READ_BATCH_SIZE = 10000 
INSERT_BATCH_SIZE = 1000 # Zilliz Cloud có thể có giới hạn về kích thước batch cho insert

def migrate_collection(collection_name):
    print(f"Bắt đầu di chuyển Collection: {collection_name}")

    # --- Kết nối đến Milvus cục bộ ---
    print(f"\nĐang kết nối đến Milvus cục bộ tại {LOCAL_MILVUS_HOST}:{LOCAL_MILVUS_PORT}...")
    try:
        connections.connect("default", host=LOCAL_MILVUS_HOST, port=LOCAL_MILVUS_PORT)
        local_collection = Collection(collection_name)
        print(f"Đã kết nối thành công đến Milvus cục bộ.")
    except Exception as e:
        print(f"Lỗi khi kết nối đến Milvus cục bộ hoặc Collection không tồn tại: {e}")
        return

    # --- Lấy Schema và thông tin Index từ Collection cục bộ ---
    print("Đang lấy Schema và thông tin Index từ Collection cục bộ...")
    local_schema = local_collection.schema
    
    # Lấy thông tin Index của trường vector chính (thường chỉ có 1 Index cho vector field)
    local_index_params = None
    if local_collection.indexes:
        # Nếu có nhiều index, bạn cần xác định index nào là của trường vector
        # Milvus 2.x thường tự động đặt tên index là _default_idx cho vector field
        for index in local_collection.indexes:
            if index.field_name == "text_dense_vector": # Tìm index của trường vector
                 local_index_params = index.params
                 break
    

    # Xác định các trường dựa trên hình ảnh của bạn
    # Giả định: recipe_id là PK, text_dense_vector là trường vector
    pk_field_name = "recipe_id"
    vector_field_name = "text_dense_vector"
    vector_field_dim = None # Sẽ được lấy từ schema

    output_fields_for_query = []
    
    # Duyệt qua schema để lấy dim của vector field và tất cả các output fields
    for field in local_schema.fields:
        output_fields_for_query.append(field.name)
        if field.name == vector_field_name:
            vector_field_dim = field.dim
        if field.name == pk_field_name and not field.is_primary:
            print(f"Cảnh báo: Trường '{pk_field_name}' được cho là khóa chính nhưng schema không đánh dấu vậy. Hãy kiểm tra lại.")

    if not vector_field_dim:
        raise Exception(f"Không tìm thấy chiều của trường vector '{vector_field_name}' trong Collection cục bộ.")
    
    print(f"Schema Collection cục bộ: {json.dumps(local_schema.to_dict(), indent=2)}")
    if local_index_params:
        print(f"Thông tin Index cục bộ: {json.dumps(local_index_params, indent=2)}")
    else:
        print("Không tìm thấy Index cho trường vector trên Collection cục bộ. Sẽ cần tạo Index trên Zilliz Cloud.")

    # --- Kết nối đến Zilliz Cloud ---
    print(f"\nĐang kết nối đến Zilliz Cloud tại {ZILLIZ_CLOUD_ENDPOINT}...")
    try:
        connections.connect(
            "zilliz_cloud",
            uri=ZILLIZ_CLOUD_ENDPOINT,
            token=ZILLIZ_CLOUD_API_KEY,
            secure=True 
        )
        print("Đã kết nối thành công đến Zilliz Cloud.")
    except Exception as e:
        print(f"Lỗi khi kết nối đến Zilliz Cloud: {e}")
        return

    # --- Tạo Collection trên Zilliz Cloud nếu chưa tồn tại ---
    zilliz_cloud_collection = None
    # Kiểm tra xem Collection có tồn tại trên Zilliz Cloud hay không
    # Đây là một cách không chính xác hoàn toàn để kiểm tra sự tồn tại của collection
    # Một cách tốt hơn là dùng `utility.has_collection(collection_name, using="zilliz_cloud")`
    from pymilvus import utility
    if utility.has_collection(collection_name, using="zilliz_cloud"):
        zilliz_cloud_collection = Collection(collection_name, using="zilliz_cloud")
        print(f"Collection '{collection_name}' đã tồn tại trên Zilliz Cloud. Số lượng entity: {zilliz_cloud_collection.num_entities}")
        # Nếu muốn xóa và tạo lại, uncomment dòng dưới và cẩn thận:
        # zilliz_cloud_collection.drop()
        # print("Đã xóa Collection cũ trên Zilliz Cloud.")
        # zilliz_cloud_collection = None # Đặt lại để tạo mới

    if zilliz_cloud_collection is None:
        print(f"Đang tạo Collection '{collection_name}' trên Zilliz Cloud...")
        # Tạo Collection với Schema giống hệt Collection cục bộ
        zilliz_cloud_collection = Collection(
            collection_name, 
            schema=local_schema,
            using="zilliz_cloud"
        )
        print(f"Đã tạo Collection '{collection_name}' trên Zilliz Cloud.")
        time.sleep(5) # Đợi một chút để Collection sẵn sàng
    
    # --- Tạo Index trên Zilliz Cloud (nếu cần) ---
    # Kiểm tra xem trường vector đã có index chưa
    if not zilliz_cloud_collection.indexes or not any(idx.field_name == vector_field_name for idx in zilliz_cloud_collection.indexes):
        print(f"Đang tạo Index cho trường '{vector_field_name}' trên Zilliz Cloud...")
        if local_index_params:
            index_params = local_index_params
        else:
            # Ví dụ Index mặc định cho vector FLOAT_VECTOR
            index_params = {
                "metric_type": "L2", # hoặc "COSINE" tùy thuộc vào cách bạn so sánh vector
                "index_type": "IVF_FLAT", 
                "params": {"nlist": 128} # Điều chỉnh nlist phù hợp với số lượng dữ liệu
            }
        
        zilliz_cloud_collection.create_index(
            field_name=vector_field_name, 
            index_params=index_params
        )
        print("Đã tạo Index trên Zilliz Cloud. Đang chờ hoàn tất...")
        time.sleep(15) # Đợi thêm chút để Index build. Có thể cần lâu hơn với dữ liệu lớn

    # --- Di chuyển dữ liệu ---
    print("\nBắt đầu di chuyển dữ liệu...")
    total_migrated_entities = 0
    offset = 0

    # Load Collection cục bộ để truy vấn
    local_collection.load()

    while True:
        # Truy vấn dữ liệu từ Milvus cục bộ
        # Giả định recipe_id là trường PK và có thể dùng cho offset
        # Nếu recipe_id là string, bạn sẽ cần một cách khác để phân trang, 
        # ví dụ: dùng auto_id hoặc đọc hết và sau đó chèn từng batch.
        # Với PK string, việc phân trang bằng offset có thể không ổn định.
        # Cách an toàn nhất là đọc tất cả nếu kích thước vừa phải, hoặc 
        # dùng các ID đã thấy để loại trừ trong các lần truy vấn tiếp theo.
        # Ở đây, ta vẫn dùng offset, giả định recipe_id là số nguyên.
        
        # Lấy tất cả các trường được định nghĩa trong schema
        res = local_collection.query(
            expr=f"{pk_field_name} >= 0", # Cần điều chỉnh nếu PK của bạn không phải số nguyên
            offset=offset,
            limit=READ_BATCH_SIZE,
            output_fields=output_fields_for_query # Sử dụng danh sách các trường từ schema
        )

        if not res:
            break

        # Chuẩn bị dữ liệu để chèn
        # PyMilvus insert nhận một list of lists (mỗi list con là giá trị của một trường)
        # hoặc một list of dicts (mỗi dict là một entity).
        # Cách list of lists (columns-first) thường hiệu quả hơn.
        
        # Khởi tạo các list trống cho từng trường
        data_to_insert_by_field = {field_name: [] for field_name in output_fields_for_query}
        
        for entity in res:
            for field_name in output_fields_for_query:
                # Đảm bảo tất cả các trường có giá trị, kể cả khi là None
                data_to_insert_by_field[field_name].append(entity.get(field_name))
        
        # Chèn vào Zilliz Cloud theo lô
        # Chuyển từ dictionary of lists sang list of lists theo thứ tự của schema
        ordered_data_for_insert = [data_to_insert_by_field[field.name] for field in local_schema.fields]

        for i in range(0, len(res), INSERT_BATCH_SIZE):
            batch_data_columns = []
            for col in ordered_data_for_insert:
                batch_data_columns.append(col[i : i + INSERT_BATCH_SIZE])
            
            try:
                # Đảm bảo Collection đã được load trước khi insert
                # Zilliz Cloud thường tự động load cho insert, nhưng tốt nhất là đảm bảo.
                # zilliz_cloud_collection.load() 
                mutation_result = zilliz_cloud_collection.insert(batch_data_columns)
                
                # count_inserted_entities = len(batch_data_columns[0]) # Lấy từ kích thước của cột đầu tiên
                # Milvus 2.x insert trả về đối tượng MutationResult
                count_inserted_entities = len(mutation_result.primary_keys) # Số lượng PK được tạo/chèn

                total_migrated_entities += count_inserted_entities
                print(f"Đã chèn {count_inserted_entities} entities. Tổng đã di chuyển: {total_migrated_entities}")
                # print(f"Mutation Result: {mutation_result}")
            except Exception as e:
                print(f"Lỗi khi chèn batch dữ liệu (Offset {offset + i}): {e}")
                # Có thể thêm logic retry hoặc ghi log chi tiết hơn
                # Quan trọng: Nếu có lỗi chèn, có thể một số entity trong batch này đã bị mất.
                break # Dừng nếu có lỗi nghiêm trọng

        offset += len(res)
        print(f"Đã đọc {offset} entities từ Milvus cục bộ.")
        if len(res) < READ_BATCH_SIZE:
            break # Hết dữ liệu

    # Sau khi chèn, flush để đảm bảo dữ liệu được ghi vào đĩa và index được cập nhật
    zilliz_cloud_collection.flush() 

    # Load Collection trên Zilliz Cloud để kiểm tra số lượng entity
    zilliz_cloud_collection.load()
    
    print(f"\nDi chuyển hoàn tất cho Collection '{collection_name}'.")
    print(f"Tổng số entity đã di chuyển: {total_migrated_entities}")
    print(f"Tổng số entity trên Zilliz Cloud: {zilliz_cloud_collection.num_entities}")

    # Xả các kết nối
    connections.disconnect("default")
    connections.disconnect("zilliz_cloud")
    print("Đã đóng kết nối Milvus cục bộ và Zilliz Cloud.")

