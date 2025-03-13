def generate_summary(self, contentdiff: str) -> dict:
    """
    生成summary的主函数
    参数:
        contentdiff: 输入的内容差异文本
    返回:
        dict: 固定格式的JSON结果
    """
    try:
        # 执行LLM链获取结果，输入需要是字典格式
        result = self.chain.invoke({"contentdiff": contentdiff})
        
        # 解析结果（假设LLM返回的是JSON字符串）
        try:
            # 假设返回的是JSON格式字符串，尝试解析
            parsed_result = json.loads(result)
            summary_content = parsed_result["summary"]["content"]
            key_points = parsed_result["summary"]["key_points"]
            word_count = parsed_result["summary"]["word_count"]
            generated_at = parsed_result["summary"]["generated_at"]
        except json.JSONDecodeError:
            # 如果返回的不是JSON，尝试手动解析纯文本
            lines = result.strip().split('\n')
            summary_content = ""
            key_points = []
            for line in lines:
                if line.startswith("Summary:"):
                    summary_content = line.replace("Summary:", "").strip()
                elif line.startswith("- "):
                    key_points.append(line[2:].strip())
            word_count = len(contentdiff.split())
            generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 创建响应对象
        response = SUMMARY_TEMPLATE.copy()
        response["summary"]["content"] = summary_content
        response["summary"]["key_points"] = key_points
        response["summary"]["word_count"] = word_count
        response["summary"]["generated_at"] = generated_at

        return response

    except Exception as e:
        # 错误处理
        error_response = SUMMARY_TEMPLATE.copy()
        error_response["status"] = "error"
        error_response["error_message"] = str(e)
        return error_response