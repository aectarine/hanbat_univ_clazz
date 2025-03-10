* PostgreSQL 설치
  * 방법 1: Postgres 직접 설치
    * 다운로드: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads -> Windows x86-64 선택
  * 방법 2: 도커 허브를 통해 설치
    * 다운로드: https://www.docker.com/products/docker-hub/
    * 이미지 다운로드: 도커 허브에서 postgres 검색 및 이미지 pull
    * 컨테이너 생성 및 실행:
    ```
    docker run -d --name test-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=0000 -p 5432:5432 postgres:latest
    ```

* OpenJDK 17 
  * 다운로드: https://jdk.java.net/java-se-ri/17-MR1
  * 설치:
    * 다운로드 및 압축해제
    * C:\ 경로로 폴더 복사
    * C:\jdk-xxx\bin 이동 및 경로 복사
    * 윈도우 검색 -> 시스템 환경 변수 편집 -> 고급 -> 환경변수 
    * -> 시스템 변수 -> 편집 -> 새로 만들기 -> 복사한 경로 붙여넣기 -> 확인
  * 설치 확인:
    * 윈도우 검색 -> cmd 입력 및 실행 -> java --version 입력 및 버전 확인


* JMETER: 5.1.1
  * 다운로드: https://archive.apache.org/dist/jmeter/binaries/
  * 실행: apache-jmeter-5.1.1/bin -> jmeter.bat 실행


* NGINX: 1.27.4
  * 다운로드: https://nginx.org/en/download.html
  * 실행: nginx-1.27.4 -> 상단 경로 클릭 -> cmd 입력 -> nginx 입력 및 실행
  * 설정: 
    * my_config 폴더 생성 -> 마우스 우클릭 -> 새로 만들기 -> 텍스트 문서 -> 새 텍스트 문서.txt 를 config.conf 로 변경
    * config.conf 우클릭 -> 메모장에서 편집 -> 아래 내용 입력 및 저장
    ```
      upstream my_server {
        least_conn;
        server localhost:8001;
        server localhost:8002;
        server localhost:8003;
      }

      server {
        listen 8010;
        server_name localhost;
  
        location / {
          proxy_pass http://my_server;
          
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Real-Port $remote_port;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header Host $http_host;
          proxy_set_header X-NginX-Proxy true;

          # 타임아웃 설정 추가
          proxy_connect_timeout 300;
          proxy_send_timeout 300;
          proxy_read_timeout 300;
          
          # 버퍼 크기 설정
          proxy_buffer_size 128k;
          proxy_buffers 4 256k;
          proxy_busy_buffers_size 256k;
          
          # 프록시 응답 버퍼링 활성화
          proxy_buffering on;
      }
    }
    ```
    * nginx-1.27.4 -> conf 폴더 이동 -> nginx.conf 우클릭 -> 메모장에서 편집 -> 맨 하단 } 윗줄에 다음 추가
    ```
    include ../my_config/config.conf;
    ```

* PM2
  * NodeJS 설치: https://nodejs.org/ko/download
  * PM2 설치: cmd -> npm i pm2 -g
  * 등록 및 구동: pm2 start main.py --interpreter python -i 4
  * 정지: pm2 stop all 또는 pm2 stop <ID 또는 앱 이름>
  * 삭제: pm2 delete all 또는 pm2 stop <ID 또는 앱 이름>
  * 목록 확인: pm2 list
  * 로그 확인: pm2 logs 또는 pm2 logs <ID 또는 앱 이름>
  * PM2 모니터링: pm2 monit
  * PC 재부팅 시 자동 시작
    * pm2 startup -> 권한 오류 발생하면 복사후 입력 및 엔터
    * pm2 save



         