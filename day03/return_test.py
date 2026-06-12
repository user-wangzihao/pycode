
#写一个函数 analyze_text(text)，要求：
#如果 text 是 None 或空字符串，用 guard clause 返回 None, "文本为空"
#正常情况返回两个值（tuple）：单词数、最长的单词
#提示：text.split() 切分单词，最长单词用 max() 配合 key=len（M1.2 学过的内置函数，这里正好复习）
#调用两次测试：一次传 "hello world from python"，一次传 ""，解包接收并打印结果

def analyze_text(text):
    if not text:
        return None,"文本为空"
    words = text.split()
    word_num = len(words)
    #print(word_num)
    word_max = max(words, key=lambda x:len(x))
    #print(word_max)
    return word_num, word_max


#result1, result2 = analyze_text("hello world from python")
result1, result2 = analyze_text("")
print(result1)
print(result2)


















