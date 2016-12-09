# 这一函数用于处理文件过大的情况，将文件分块写入
# 写入文件的路径由open函数决定，wb+代表以二进制读写模式打开
# with as是一种异常处理机制，在这里是防止文件打开失败一类的错误


def handle_upload_file(file):
    with open('name.txt', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
