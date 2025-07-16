import os
import sys
import xml.etree.ElementTree as ET

def burp_xml_to_sqlmap_request(burp_xml_file, output_dir="sqlmap_requests_from_xml"):
    """
    将Burp Suite导出的XML请求文件转换为SQLmap可识别的请求文件。

    Args:
        burp_xml_file (str): Burp Suite导出的XML文件路径。
        output_dir (str): 保存SQLmap请求文件的输出目录。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        tree = ET.parse(burp_xml_file)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"错误: 文件未找到 '{burp_xml_file}'。请检查文件路径是否正确。")
        return
    except ET.ParseError as e:
        print(f"错误: 解析XML文件失败。请检查文件格式是否正确。错误信息: {e}")
        return

    # 查找所有的 <item> 元素
    items = root.findall('item')
    if not items:
        print(f"在文件 '{burp_xml_file}' 中未找到任何 <item> 元素，请检查文件内容。")
        return

    print(f"检测到 {len(items)} 个请求。")

    for i, item in enumerate(items):
        request_element = item.find('request')
        
        if request_element is not None and request_element.text is not None:
            # 获取请求的原始文本内容，即CDATA部分
            raw_request = request_element.text.strip()

            if not raw_request:
                print(f"警告: 索引 {i+1} 的请求内容为空，跳过。")
                continue

            output_filename = os.path.join(output_dir, f"request_{i+1}.req")
            
            try:
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    outfile.write(raw_request)
                print(f"已生成文件: {output_filename}")
            except IOError as e:
                print(f"写入文件 {output_filename} 失败: {e}")
        else:
            print(f"警告: 索引 {i+1} 的 <request> 元素未找到或内容为空，跳过。")

    print("\n所有请求转换完成！")

---

### **如何使用这个修改后的工具**

1.  **保存代码：** 将上述代码保存为 `.py` 文件，例如 `burp_xml_converter.py`。
2.  **运行脚本：** 打开您的终端或命令提示符，然后以这种格式运行脚本，将您的 Burp 导出 XML 文件作为第一个参数：

    ```bash
    python burp_xml_converter.py burp_exported_requests.xml
    ```
    *请将 `burp_exported_requests.xml` 替换为您实际的 Burp XML 文件路径。*

    如果您想指定不同的输出目录，可以考虑添加第二个参数，或者让脚本始终输出到默认目录。为了简单起见，当前版本默认输出到 `sqlmap_requests_from_xml` 文件夹。

---

### **示例：命令行参数处理**

在 `if __name__ == "__main__":` 块中，我们将修改代码以检查命令行参数的数量。

```python
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python burp_xml_converter.py <burp_exported_xml_file>")
        print("例如: python burp_xml_converter.py burp_requests.xml")
        sys.exit(1) # 退出程序，表示错误
    
    burp_file_path = sys.argv[1] # 第一个参数是脚本名，第二个是我们要的文件路径
    
    # 调用函数进行转换
    burp_xml_to_sqlmap_request(burp_file_path)

    print("\n💡 接下来你可以在SQLmap中使用这些文件，例如：")
    print("   sqlmap -r sqlmap_requests_from_xml/request_1.req --dbs --batch")