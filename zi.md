
| Chức năng        | Cú pháp                                             | Mô tả                       |
| ---------------- | --------------------------------------------------- | --------------------------- |
| Hiển thị text    | `<p th:text="${name}"></p>`                         | Thay nội dung thẻ bằng biến |
| Gán link         | `<a th:href="@{/home}"></a>`                        | Tạo URL                     |
| Gán src          | `<img th:src="@{/img.png}" />`                      | Gán đường dẫn ảnh           |
| If               | `<p th:if="${age > 18}"></p>`                       | Hiển thị nếu đúng           |
| Unless           | `<p th:unless="${age > 18}"></p>`                   | Hiển thị nếu sai            |
| Loop             | `<li th:each="item : ${list}"></li>`                | Lặp danh sách               |
| Loop + index     | `<li th:each="item, stat : ${list}"></li>`          | Có index                    |
| Form object      | `<form th:object="${user}"></form>`                 | Bind object                 |
| Input field      | `<input th:field="*{name}" />`                      | Bind field                  |
| Fragment         | `<div th:fragment="header"></div>`                  | Tạo component               |
| Include fragment | `<div th:replace="file :: header"></div>`           | Gọi component               |
| Switch           | `<div th:switch="${role}"></div>`                   | Điều kiện nhiều case        |
| Case             | `<p th:case="'admin'"></p>`                         | Nhánh case                  |
| Default case     | `<p th:case="*"></p>`                               | Mặc định                    |
| Class động       | `<div th:class="${isActive} ? 'on' : 'off'"></div>` | Class động                  |
| Value            | `<input th:value="${name}" />`                      | Gán value                   |
| Disabled         | `<input th:disabled="${flag}" />`                   | Disable input               |
| Checked          | `<input type="checkbox" th:checked="${flag}" />`    | Check checkbox              |
| Inline text      | `[[${name}]]`                                       | Dùng trong text             |
| Inline JS        | `/*[[${name}]]*/`                                   | Dùng trong JS               |

---
- `${}` → lấy biến từ model
- `*{}` → dùng trong form (`th:object`)
- `@{}` → dùng cho URL
