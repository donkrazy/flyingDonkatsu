# Requirements  
python3.6  
requests  


# QuickStart  
python3 main.py  

# Idea  
1. token과 seed를 받아온 후 5개의 Crawler thread를 생성하여 feature에 대해 get, post/delete 수행  
2. ConnectionError 발생시 1초 sleep했다가 다시 수행  
5. 가져온 next_url이 기존 url과 같을 시 1초 sleep  
3. urllib.request 이용하다가 post요청이 잘 안되어 requests 모듈로 일부 교체  
4. Crawler workflow: init -> [ get_document -> manage_image() -> manage_feature() ] -> stop  
6. HTTP 401 Error 발생시 토큰 만료로 간주하고 프로세스 종료  
5. simple work checker로 시간대별 작업량 체크  

# TODO  
1. HTTP 403 Error 발생시 토큰 파일에서 읽지 말고 responsebody에서 읽기  
2. 스레드 종료 잘 안됨  
3. time checker visualization  
4. document 리젠 주기 파악, 1초 sleep이 최선이었을까,   
5. 가끔씩 뜨는 네트워크 에러  
6. images, features 내부 DB나 set()으로 중복 관리  
7. features DETELE 요청시 json 양식 맞추기..id만 남겨야함  
8. 상위권 랭크와 비교해서 API호출횟수는 비슷했으나 올바른데이터(A값)이 낮음  
9. refactoring: 클래스 request 객체, urllib.request 제거  
