Service modules are shared Python modules that can be used across
multiple apps. Each service module must NOT depend upon
streamlit or complex types in any fashion - otherwise it's a helper.

They are stored in the `services` directory and can be imported into any app using the following syntax:

    ```python
    from services import my_service
    ```
