import sys
import jieba.analyse
import hashlib
from learn.text_analyse.crime_judge import *


def text_analyse():
    # 打开文件并计算MD5码，判断案例是否在库中
    file_text = open("D:\\mydjango\\name.txt", 'r')
    content = file_text.read()
    tex_md5 = hashlib.md5()
    tex_md5.update(content.encode('utf-8'))
    file_md5 = tex_md5.hexdigest()
    print("案件的MD5码为："+file_md5)
    case_con = sqlite3.connect('case.db')
    case_cur = case_con.execute("SELECT count(*) FROM sqlite_master where type='table' and name = \"LAW_CASE\";")
    ans = case_cur.fetchone()[0]
    if ans == 0:
        case_con.execute("CREATE TABLE LAW_CASE (MD5 TEXT PRIMARY KEY NOT NULL,\
        CONTENT TEXT,COURT TEXT,CASE_TYPE TEXT,\
        REFERENCE TEXT,FEATURE TEXT,KEYWORD TEXT);")
        case_con.commit()
    case_cur = case_con.execute("SELECT count(*) FROM LAW_CASE WHERE MD5 = "+"'"+file_md5+"'")
    exist = case_cur.fetchone()[0]
    if exist:
        print("案例已存在,案例要素如下:")
        query = "SELECT COURT,CASE_TYPE,REFERENCE,FEATURE,KEYWORD FROM LAW_CASE WHERE MD5 = "+"'"+file_md5+"'"
        case_cur = case_con.execute(query)
        result = case_cur.fetchone()
        print("判决（裁定）法院：", result[0])
        print("文书类型：", result[1])
        print("此案例涉及的法律为：", result[2])
        print("此案例特征为：", result[3])
        print("案件关键词Top10：", result[4])

        analyse_res = ["案例已存在", file_md5, result[0], result[1], result[2], result[3],result[4]]
        return analyse_res

    # 判断案例要素：
    # 1.判决法院
    # 2.文书类型
    # 3.案例涉及法律
    # 4.案件特征：案由（民事案件）or 罪行（刑事案件）
    # 其中3,4通过比对数据库实现
    d_tex = content.split()
    court = d_tex[0]
    print("判决（裁定）法院："+court)
    case_type = d_tex[1]+d_tex[2]+d_tex[3]+d_tex[4]+d_tex[5]
    print("文书类型："+case_type)
    law_con = sqlite3.connect('law.db')
    cursor = law_con.execute("SELECT LAWS from LAW")
    law = []
    reference = []
    cause = []
    for row in cursor:
        law.append(row[0])
    for i in range(0, len(law)):
        law[i] = law[i].replace("\n", "")
        n = content.count(law[i])
        if n > 0:
            reference.append(law[i])
            if law[i] == "中华人民共和国刑事诉讼法":
                cause = crime_judge(content)
            elif law[i] == "中华人民共和国民事诉讼法":
                cause = cause_judge(content)
    reference = " ".join(reference)
    print("此案例涉及的法律为："+reference)
    num = len(cause)
    cause_all = " ".join(cause)
    print("此案例特征为："+cause_all)
    print("案由（罪行）总数为：", num)
    law_con.close()

    # 调用分词组件，加载用户词典及停止词词库
    # 使用TF—IDF算法提取关键词，不显示词频，限制其词性为名词
    jieba.load_userdict("D:\\mydjango\\learn\\text_analyse\\law_dict.txt")
    jieba.analyse.set_stop_words("D:\\mydjango\\learn\\text_analyse\\law_stop_done.txt")
    tag = jieba.analyse.extract_tags(content, 10, False, "vn")
    keyword = []
    for t in tag:
        tem = str(t)
        keyword.append(tem)
    keyword_all = " ".join(keyword)
    print("案件关键词Top10："+keyword_all)

    # 查询案由是否在案由库中，若不在以案由（或罪行）建立特征库
    # 将案例中不重复的关键词添加进特征库
    key_con = sqlite3.connect('Keywords.db')
    index_con = sqlite3.connect('Keyword_index.db')
    count_all = []
    key_all = []
    cause_count = 0
    for g in cause:
        same_count = 0
        same_word = []
        key_cur = key_con.execute("SELECT count(*) FROM sqlite_master where type='table' and name= ?;", ([g]))
        ans = key_cur.fetchone()[0]
        if ans == 0:
            key_con.execute("CREATE TABLE "+g+"(KEYWORD    TEXT  PRIMARY KEY  NOT NULL)")
            key_con.commit()
            print("以案例特征 "+g+" 建立特征词库。")
        else:
            print("案例特征 "+g+" 已存在对应特征词库。")
        for i in range(0, len(keyword)):
            key_cur = key_con.execute("SELECT count(*) FROM "+g+" where KEYWORD = \""+keyword[i]+"\";")
            has_key = key_cur.fetchone()[0]
            if has_key == 0:
                key_con.execute("INSERT INTO "+g+" (KEYWORD) VALUES(\"" + keyword[i]+"\");")
                key_con.commit()
                print("添加关键词 " + keyword[i] + " 进入特征词库。")
                index_cur = index_con.execute("SELECT count(*) \
                FROM sqlite_master where type='table' and name= ?;", ([keyword[i]]))
                ans = index_cur.fetchone()[0]
                if ans == 0:
                    index_con.execute("CREATE TABLE "+keyword[i]+"(MD5_INDEX TEXT PRIMARY KEY);")
                    index_con.commit()
                query = "SELECT count(*) FROM " + keyword[i] + " WHERE MD5_INDEX = \""+file_md5+"\";"
                index_cur = index_con.execute(query)
                case_exist = index_cur.fetchone()[0]
                if case_exist == 0:
                    index_con.execute("INSERT INTO " + keyword[i] + "(MD5_INDEX) VALUES(\"" + file_md5+"\");")
                    index_con.commit()
                elif (case_exist > 0 and cause_count == 0) or (case_exist > 1 and cause_count > 0):
                    index_con.execute("INSERT INTO " + keyword[i] + "(MD5_INDEX) VALUES(\"" + file_md5 + "\");")
                    index_con.commit()

            else:
                print("关键词 " + keyword[i] + " 已加入特征词库。")
                query = "SELECT count(*) FROM " + keyword[i] + " WHERE MD5_INDEX = \"" + file_md5 + "\";"
                index_cur = index_con.execute(query)
                case_exist = index_cur.fetchone()[0]
                if case_exist == 0:
                    index_con.execute("INSERT INTO " + keyword[i] + "(MD5_INDEX) VALUES(\"" + file_md5 + "\");")
                    index_con.commit()
                elif (case_exist > 0 and cause_count == 0) or (case_exist > 1 and cause_count > 0):
                    index_con.execute("INSERT INTO " + keyword[i] + "(MD5_INDEX) VALUES(\"" + file_md5 + "\");")
                    index_con.commit()
                same_count += 1
                same_word.append(keyword[i])
                index_con.commit()
        count_all.append(same_count)
        key_all.append(same_word)
        cause_count += 1

    index_con.close()
    key_con.close()
    for i in range(0, len(cause)):
        print("特征", cause[i], " 重叠关键词数：", str(count_all[i]))
        if key_all[i]:
            print("重叠关键词为：", " ".join(key_all[i]))

    query = "INSERT INTO LAW_CASE (MD5,CONTENT,COURT,CASE_TYPE,REFERENCE,FEATURE,KEYWORD) \
    VALUES('" + file_md5 + "','" + content + "','" + court + "','" + case_type + "\
    ','" + reference + "','" + cause_all + "','" + keyword_all + "');"
    case_con.execute(query)
    case_con.commit()
    case_con.close()
    analyse_res = ["新案例，已收录 ", file_md5, court, case_type, reference, cause_all, keyword_all]
    return analyse_res

print(text_analyse())