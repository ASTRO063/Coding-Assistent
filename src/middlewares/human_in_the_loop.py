
from langchain.agents.middleware import HumanInTheLoopMiddleware
# from tools.file_tool import read_file, write_file

middlewares=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "read_file": False,
                "write_file": True,
            },
            description_prefix="Tool execution requires approval",
        ),
    ]