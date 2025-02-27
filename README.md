![OpenJDK](https://developers.redhat.com/sites/default/files/styles/keep_original/public/openjdk-basic-featured-image.png?itok=IOXZF7iv){:width="300px" height="200px"}
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



         