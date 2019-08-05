import requests
import re
from bs4 import BeautifulSoup

#作业部分，支持任何语言
def encrypt(string):
	result = ""
	for char in string:
		#如果是文字或者数字则转成ascii
		if char.isalnum():
			result += str(ord(char))
		#若不是文字则保持不变
		else:
			result += char

		#加上分隔符 |
		result += '|'

	return result

def decrypt(string):
	result = ""
	#分割字符串，并且去除末尾为空的元素
	temp_list = string.split("|")[:-1]

	for each in temp_list:
		#如果是数字则转成文字和阿拉伯数字
		if each.isdigit():
			result += chr(int(each))
		#若不是数字则保持不变
		else:
			result += each

	return result


#自己的加密方法
#到在线汉语字典网 http://xh.5156edu.com/index.php 中搜索该汉字，获取该汉字搜索页面url中的数字编号作为汉字密码数字部分
#一个汉字的密码为 c + 数字密码， 如 "好" 的编码为: c6348
#如果不是汉字则为 e + ascii码
#分隔符为 | 
#不支持其他语言

def get_cnumber(char):
	#获取网页的url
	headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
	url = 'http://xh.5156edu.com/index.php'
	data = data = {'f_key':char.encode('gbk'),'f_type':'zi'}
	resp = requests.post(url,data=data,headers=headers)

	#从url中获取数字
	reg = '/([0-9]+).html'
	return re.findall(reg, resp.url)[0]


def get_chinese_char(num):
	#获取html
	url = 'http://xh.5156edu.com/html3/%s.html' % num
	headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
	resp = requests.get(url,headers=headers)
	resp.encoding = 'gbk'

	#抓取汉字信息
	soup = BeautifulSoup(resp.text,'html.parser')
	target_char = soup.find('td',class_='font_22').text

	return target_char



def my_encrypt(string):
	length = len(string)
	result = ""
	for i in range(length):
		#如果是标点符号，则保持不变
		if not string[i].isalnum():
			result += string[i]

		#如果是数字或者英文，则转为ascii码
		elif ord(string[i]) < 127 :
			result += 'e'
			result += str(ord(string[i]))

		#如果是中文，则去网站抓取数字
		else:
			result += 'c'
			result += get_cnumber(string[i])

		#加上分隔符 |
		result += '|'

		print('已完成%.2f%%' % ((i+1)*100/length), end='\r')

	print('恭喜你，加密成功！')
	return result


def my_decrypt(string):
	result = ""
	#分割字符串，并且去除末尾为空的元素
	temp_list = string.split('|')[:-1]
	length = len(temp_list)

	for i in range(length):
		#如果开头为e，则为数字或者英文，采用ascii解密
		if temp_list[i].startswith('e'):
			result += chr(int(temp_list[i][1:]))
		#如果开头为c，则为中文，则去网页抓取中文汉字
		elif temp_list[i].startswith('c'):
			result += get_chinese_char(temp_list[i][1:])
		#否则为标点符号，保持不变输出
		else:
			result += temp_list[i]

		print('恭喜你，已完成%.2f%%' % ((i+1)*100/length), end='\r')

	print('解密成功！')
	return result



def main():
	print('请选择进行加密的方式>>>>>>')
	print('输入1，则进行作业加密。')
	print('输入2，则进行拓展加密。')
	choice = input('请输入>>>>>>>')

	#进行作业加密
	if choice == '1':
		encrypt_func = encrypt
		decrypt_func = decrypt
	#进行拓展加密
	elif choice == '2':
		encrypt_func = my_encrypt
		decrypt_func = my_decrypt
	#无效输入，程序退出
	else:
		print('无效的输入。')
		return

	input_message = input('请输入需要加密的文字>>>>>>>')
	print("正在进行加密...")
	encrypt_result = encrypt_func(input_message)
	print("加密后的结果为>>>>>>%s" % encrypt_result)
	print("-"*15)

	print("正在进行解密...")
	print("解密后的结果为>>>>>>>%s" % decrypt_func(encrypt_result))


if __name__ == '__main__':
	main()
