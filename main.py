import os
import pypandoc
import uvicorn
from litestar import Litestar, get, post



@get("/")
async def index() -> str:
    return "Hello, world!"


@post("/general_docx")
async def general_docx(context: str) -> dict[str, int]:
    try:
        with open("", mode='') as f:
            ...
        return {"status": "success"}
    except Exception as e:
        return {
            "status": "success",
            "msg": str(e)
        }    


app = Litestar([index, general_docx])

if __name__ == "__main__":
    uvicorn.run("main:app", port=8901, log_level="info")

def markdown_to_word_advanced(md_text, output_path="output.docx"):
    """
    使用pandoc将Markdown转换为Word文档
    """
    try:
        # 将Markdown文本写入临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
            temp_md.write(md_text)
            temp_md_path = temp_md.name
        
        # 使用pandoc转换
        pypandoc.convert_file(
            temp_md_path,
            'docx',
            outputfile=output_path,
            extra_args=[
                '--wrap=auto',
                '--highlight-style=tango',
                '--extract-media=.',
                f'--resource-path={os.getcwd()}'
            ]
        )
        
        print(f"✅ Word文档已保存至: {output_path}")
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        
    finally:
        # 清理临时文件
        if 'temp_md_path' in locals() and os.path.exists(temp_md_path):
            os.unlink(temp_md_path)

