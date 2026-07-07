# UiBot中通过Python代码生成图片Base64编码（需先导入base64模块）
import base64
def img_html(img_path):
    # 替换为你的本地图片路径（绝对路径）

    with open(img_path, "rb") as f:
        # 生成Base64编码字符串
        img_base64 = base64.b64encode(f.read()).decode("utf-8")
    # 拼接HTML图片标签（格式：data:image/图片格式;base64,编码字符串）
    # 支持png/jpg/jpeg/gif，需与图片实际格式一致
    img_html_str = f'<img src="data:image/jpg;base64,{img_base64}" width="300" height="auto">'
    return img_html_str