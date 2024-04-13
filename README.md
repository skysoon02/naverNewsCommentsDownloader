# Naver News Comments Downloader

## Require
pip install pymysql

## 사용법


##DB

설치
sudo apt-get update
sudo apt-get isntall mysql-server


실행
service mysql start


계정 추가
1. 관리자 권한으로 mysql 접속
mysql -u root -p
또는
sudo mysql -u root -p

2. user db사용
use mysql

3. 
계정 생성. 대문자는 변수
create user USERNAME
create user USERNAME@localhost identified by 'PASSWORD';

4. DB생성
create database DBNAME default character set utf8;

5. DB 권한 부여
grant all privileges on DBNAME.* to USERNAME@localhost


show databases;
show table status;


newsTitle 폴더에 {뉴스 이름}\t{채널} 형식으로 이루어진 파일들을 넣어서 main.py 실행
