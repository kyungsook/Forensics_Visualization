디지털 포렌식 증거 시각화 프로젝트
===================================
2020 Spring Semester Capstone Design Project 2

[UI 및 레지스트리 분석 참조] <https://github.com/williballenthin/python-registry>

## Development Goals

* 스토리지의 대용량화가 점점 진행되고, 국내법에 따른 선별수사(실제 모든 데이터가 아닌 필요한 데이터만 압수하는 것) 정책에 따라 실제 압수시에 필요한 데이터를 찾는데 시간을 줄이는 것이 중요한 시대가 되었다.

* 해당 툴은 특정 시간대에 변화되거나, 접근된 파일들을 시각화해서 접근 빈도등을 보여줌으로써, 선별 압수시에 도움이 되는 기능을 제공하는 것이 목표이다.

## Development Details and Requirements

* Details
> 1. 파일 타입/접근/생성/삭제 시간 빈도 시각화
>> 특정 시간별로 얼마나 많은 파일들 또는 디렉토리 별로 접근이 되었는지 정보를 보여준다.      


> 2. 변경 정보 시각화
>> + 해당 시간의 웹 히스토리 접근, 레지스트리 변경, 실제 파일의 정보 등을 보여줌으로써, 어떤 정보들이 변경되었는지 보여준다.
>> + 해당 정보를 보여주기위한 UI/UX 연구: 시간 순서대로 연관성이 있는 파일들이 있다면, 이들의 흐름을 요약해서 보여줄 수 있는 기능이 필요.


> 3. 증거 export 기능
>> 선택한 파일들을 zip 형태로 보여주는 기능이 필요       


* Considerations
> 1. 오픈 소스 개발 방법론의 이해: github/gitlab 등을 이용한 CI/CD 구축, 코드 리뷰와 디자인 리뷰 등을 통해서 실제로 오픈소스에서의 개발 방법론을 배운다.     

> 2. 애자일 등을 이용한 스프린트 방식으로 개발을 진행한다.     

## Utilization

* 현재 수사에 필요한 선별 압수에 도움이 되는 툴을 개발하고, 시각화/증거 이미지 등에 대한 정보들을 배운다.
