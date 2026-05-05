---
description: Describe when these instructions should be loaded by the agent based on task context

---

- Với mỗi chỉnh sửa liên quan đến codebase từ yêu cầu của người dùng hoặc plan được tạo bởi agent, tiến hành dùng các MCP tools để research và phân tích codebase hiện tại, đảm bảo rằng mọi chỉnh sửa đều dựa trên sự hiểu biết sâu sắc về codebase hiện tại, tránh việc tạo ra code mới mà không hiểu rõ về codebase hiện tại.
- Luôn sử dụng các MCP tools để quản lý context, memory, và các nguồn lực khác của agent, đảm bảo rằng mọi chỉnh sửa đều được thực hiện trong bối cảnh phù hợp và dựa trên thông tin chính xác.
- Luôn thực thi ở môi trường 'fruit_env'.
- Với các debug liên quan đến GUI, luôn sử dụng các MCP tools có khả năng tương tác với GUI và quan sát output của terminal từ đó khoanh vùng lỗi một cách chính xác -> research thêm về các lỗi đó trước khi thực hiện chỉnh sửa codebase.
- Luôn đảm bảo rằng mọi chỉnh sửa đều được thực hiện dựa trên sự hiểu biết sâu sắc về codebase hiện tại, tránh việc tạo ra code mới mà không hiểu rõ về codebase hiện tại.
- Đối với các thư viện người dùng yêu cầu, luôn research documentation của thư viện đó trước khi thực hiện chỉnh sửa codebase, đảm bảo rằng mọi chỉnh sửa đều phù hợp với version của thư viện mà người dùng đang sử dụng.

- Không bao giờ được phép chạy môi trường khác ngoài 'fruit_env' khi không có sự cho phép rõ ràng từ người dùng.

- Mỗi lệnh excecuate luôn phải được thực hiện trong môi trường 'fruit_env', trừ khi có sự cho phép rõ ràng từ người dùng để chạy môi trường khác. Nếu có yêu cầu chạy môi trường khác, hãy đảm bảo rằng bạn đã hiểu rõ về môi trường đó và đã được sự cho phép rõ ràng từ người dùng trước khi thực hiện lệnh.