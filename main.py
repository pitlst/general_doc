import datetime
import os
import pypandoc
import uvicorn
import aiofiles
from pathlib import Path
from litestar import Litestar, get, post
from litestar.exceptions import NotFoundException
from litestar.response import File
from pydantic import BaseModel

SOURCE_PATH = Path('./source')
SOURCE_PATH = SOURCE_PATH.resolve()
TRARGET_PATH = Path('./target')
TRARGET_PATH = TRARGET_PATH.resolve()

# 确保目录存在
SOURCE_PATH.mkdir(exist_ok=True)
TRARGET_PATH.mkdir(exist_ok=True)

class TextPayload(BaseModel):
    context: str

def validate_and_resolve_path(requested_path: str) -> Path:
    """验证并解析路径，防止目录遍历攻击"""
    if not requested_path:
        return TRARGET_PATH
    # 规范化路径并解析为绝对路径
    try:
        # 移除开头的斜杠
        requested_path = requested_path.lstrip("/")
        # 使用Pathlib安全地拼接路径
        resolved = (TRARGET_PATH / requested_path).resolve()
        # 安全检查：确保解析后的路径仍在基础目录内
        if not str(resolved).startswith(str(TRARGET_PATH)):
            raise RuntimeError("访问被拒绝：非法路径")
        return resolved
    except Exception as e:
        raise RuntimeError(f"路径解析错误: {str(e)}")

@get("/get_docx/{path:str}")
async def get_docx(path: str)-> File | dict[str, str]:
    """列出目录内容或提供文件下载"""
    try:
        file_time = datetime.datetime.strptime(path.split(".")[0], "%Y-%m-%d_%H:%M:%S")
        request_time = datetime.datetime.now() - datetime.timedelta(days=1)
        target_path = validate_and_resolve_path(path or "")
        # 超时删除文件
        if file_time < request_time:
            os.remove(target_path)
        if not target_path.exists():
            raise NotFoundException(f"路径不存在: {path}")
        if not target_path.is_file():
            raise NotFoundException(f"路径不是文件: {path}")
        return File(
            path=target_path,
            filename=target_path.name,
            stat_result=target_path.stat()
        )
    except Exception as e:
        return {
            "status": "error",
            "msg": str(e)
        } 


@post("/general_docx")
async def general_docx(data: TextPayload) -> dict[str, str]:
    try:
        # 生成路径信息
        now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        source_file_path = SOURCE_PATH / f"{now_str}.md"
        target_file_path = TRARGET_PATH / f"{now_str}.docx"
        
        context = data.context
        context = context.replace('\\n', '\n')
        print(context)
        # 暂存调用的文件
        async with aiofiles.open(source_file_path, mode='w') as f:
            await f.write(context)
        # 使用pandoc转换
        pypandoc.convert_file(
            source_file_path,
            'docx',
            outputfile=target_file_path,
            extra_args=[
                '--wrap=auto',
                '--highlight-style=tango',
                '--extract-media=.',
                f'--resource-path={os.getcwd()}'
            ]
        )
        # 生成url
        return {
            "status": "success",
            "url": f"{now_str}.docx"
        }
    except Exception as e:
        return {
            "status": "error",
            "msg": str(e)
        }    


app = Litestar([get_docx, general_docx])

if __name__ == "__main__":
    uvicorn.run("main:app", port=8901, log_level="info")

