## 1 공정한 게임 생태계의 위기

```
1.1 치트(Cheat) 비중의 급증과 산업적 위협
최근 글로벌 게임 산업에서 부정행위는 단순한 매너 문제를 넘어 연간 약
290 억 달러(한화 약 42 조 원) 규모의 손실을 초래하는 거대한 산업적 위협이
된다１. 특히 실시간 경쟁이 핵심인 장르에서 치트는 게임의 공정성을
무너뜨리고 재미를 반감시키는 등의 치명적인 문제를 일으킨다.
```
```
1.1.1 치트의 대중화 및 고도화
과거 일부 유저의 일탈이었던 치트는 이제 치트 제작자, 블랙 마켓 중개인,
최종 사용자 등으로 역할이 명확히 나뉘는 비즈지스 모델이 갖춘 완전한
산업으로 발전했다. 치트가 이제 개인의 재미를 넘어 금전적 이득을
목적으로 하는 조직적인 범죄 및 비즈니스의 영역으로 넘어갔다. 이러한
발전에 따라 이제는 누구나 치트에 쉽게 접근할 수 있게 되었다.２
```
```
1.1.2 유저 이탈 가속화 및 경제적 손실
Forbes 보고서에 따르면, 10 명 중 9 명의 게이머는 부정행위자 때문에
불쾌한 경험을 한적이 있다고 한다. 공정성이 무너진 게임에서 일반
유저는 극심한 피로감을 느끼며 이는 곧 대규모 이탈로 이어진다. 유저
이탈은 매출 감소로 직결될 뿐만 아니라, 치트를 막기 위한 운영 인건비와
서버 리소스 낭비 등 막대한 추가 비용을 발생한다^ ３
```
```
1.2 기존 안티 치트 솔루션의 한계
현재 시장을 점유하고 있는 기술 중심의 안티 치트 방식은 기술적, 사회적
관점에서 한계에 부딪히고 있다.
```
```
1.2.1 프라이버시 침해와 유저 반발
커널 레벨에서 동작하는 안티 치트가 유저의 개인정보를 과도하게
수집하고 시스템 권한을 장악함. 이는 유저들 사이에서 보안 우려와
프라이버시 침해 논란을 불러일으키며 브랜드 이미지에 타격을 준다.４５
```
```
1.2.2 지능형 우회 기술의 확산
모바일 환경에서는 루팅(Rooting) 및 에뮬레이터 변조를 통한 우회가
빈번하다. 특히 클라이언트의 메모리를 직접 건드리지 않고 화면 픽셀을
분석하여 조작하는 외부 AI 에임봇과 같은 기술은 기존의 정적 분석
```

## 방식으로는 탐지가 어렵다.４６７

## 1.3 개발 목적 및 방향

## 따라서 본 기획은 기존의 '파일 및 프로세스 감시' 방식에서 벗어나, '유저의

행위 분석(Behavioral Analysis)'에 집중한 AI 기반 안티 치트 시스템을 제안한다
.
2 AI 기반 안티 치트 및 XAI
안드로이드 TPS 게임의 안티 치트 시스템에서 AI 및 XAI(설명 가능한 AI)를 활용한
구체적인 탐지 시나리오와 그에 따른 장점은 다음과 같다.

```
2.1 로그 기반 비정상 조작 탐지 및 SHAP 분석
```
```
2.1.1 탐지 과정
플레이어의 에임 이동 경로, 반응 속도, 클릭 패턴 등의 로그를 수집하여
LSTM이나 CNN과 같은 딥러닝 모델(또는 머신러닝)로 분석한다.８９
```
```
2.1.2 XAI 적용 (근거 시각화)
모델이 특정 유저를 치터로 판단했을 때, 블랙박스처럼 결과만 내놓는
것이 아니라 SHAP(또는 LIME) 기법을 사용하여 "왜 핵으로 판단했는지"에
대한 Feature Importance(특성 중요도)를 제공한다. 해당 정보로 "해당
유저의 플레이에서 '0.01초 만에 에임이 적의 헤드셋으로 꺾임(반응 속도)',
'비인간적인 터치 지속 시간' 피처가 부정행위 판별에 80% 이상의
기여도를 보였음" 등을 수치와 그래프로 제시 가능하다.
```
```
Figure 1. shap의 Feature Importance 예시
```

## 2.2 LLM 기반의 운영자용 자동 요약 보고서 생성

## 2.2.1 생성 과정
AI가 탐지한 결과와 XAI가 생성한 시각적/수치적 근거 데이터를 LLM(대형언어 모델) 시스템에 전달한다. 여기에 사내 운영 정책 및 제재 기준을RAG(검색 증강 생성) 방식으로 연동한다.

## 2.2.2 XAI 적용 (자연어 설명)

수많은 로그를 운영자가 직접 볼 필요 없이, LLM이 XAI의 결과를 바탕으로 자연어 형태의 브리핑 보고서를 자동 생성한다. "해당 유저는 최근 3 판 동안 비정상적인 에임 보정(기여도 1 위)과 초인적인 반응
속도가 발생했으며, 사내 운영 정책 3 조에 의거하여 즉각적인 계정 제재가 권장됨."이라는 요약 리포트가 대시보드에 출력한다.

## 2.3 AI 및 XAI 기반 안티 치트 도입의 핵심 장점

```
2.3.1 명확한 제재 근거 확보 및 오탐(False Positive) 논란 해소
기존 AI 모델은 정확도가 높아도 결과를 도출한 이유를 알 수 없는
블랙박스였기 때문에 AI 제재 시 유저들의 반발을 살 가능성이 높음.
XAI는 특정 플레이어가 어떤 특징 때문에 적발되었는지 시각적/수치적
증거를 명확히 제시함. 유저가 억울함을 호소하며 소명을 요청할 때,
고객센터에서 이 근거를 바탕으로 투명하게 대응할 수 있어 운영의
신뢰도가 크게 상승함.１０
```
```
2.3.2 프라이버시 침해 없는 비침습적(Non-intrusive) 탐지
뱅가드(Vanguard)와 같이 사용자 PC나 모바일 기기의 커널 레벨까지
감시하는 기존 안티 치트 솔루션은 유저의 개인정보 침해 논란과 시스템
크래시 문제를 일으킨다. 서버로 전송되는 로그만 분석하는 AI 방식을
채택하면, 사용자의 기기에 깊이 관여하지 않고도 지능형 치트를
효과적으로 잡아낼 수 있다.５
```
```
2.3.3 지능형/외부 기기 우회 치트 선제적 방어
최근 유행하는 외부 캡처 보드와 AI를 결합한 에임봇이나 하드웨어
변조(DMA) 치트는 클라이언트의 메모리를 변조하지 않기 때문에 기존의
시그니처 기반 탐지로는 막을 수 없다. 행동(로그) 패턴 자체를 분석하는
```

## AI는 특정 해킹 프로그램의 시그니쳐를 몰라도 인간의 한계를 벗어나는비정상적인 움직임을 실시간으로 포착하여 알려지지 않은 새로운 치트까지대응할 수 있다.８

## 2.3.4 AI 모델의 오류 디버깅 및 지속적 최적화

## XAI는 단순히 유저를 제재하는 데 그치지 않고, AI 개발팀이 모델을개선하는 데 핵심적인 역할을 한다. 예를 들어, XAI 히트맵 분석을 통해"AI가 정상적인 유저의 '붉은색 조준점'을 치트 프로그램의 UI로 착각하여오탐지하고 있다"는 사실을 발견하면, 개발자는 즉시 해당 데이터를수정하여 모델의 정확도를 높이고 무고한 피해자 발생을 막을 수 있다.또한, 중요도가 떨어지는 피처를 제거하여 모델을 경량화하고 처리 속도를개선할 수 있다.１０

## 3 데이터셋 구성 및 샘플 데이터 분석

## 3.1 샘플 데이터셋 선정 및 개요현재는 개발 초기라 인공지능을 개발하거나 테스트할 데이터셋이 부족한상황이다. 따라서 공개 되어있는 게임 관련 데이터를 활용하기로 한다. 초기

```
모델 설계 및 알고리즘 검증을 위해 Hugging Face에 공개된 CS2CD(Counter-
Strike 2 Cheating Dataset)를 샘플 데이터로 활용한다. 본 데이터셋은
Transformer 기반 탐지 모델인 'AntiCheatPT' 연구에 사용된 것으로, 시계열
행위 분석에 최적화되어 있다. 실제 매치에서 추출된 플레이어의 텔레메트리
데이터로, 정상 유저와 치트 유저(에임봇, 월핵 등)의 행위가 라벨링되어
있다.１１１２１３.
```
```
3.2 샘플 데이터셋 상세 분석
```
```
3.2.1 Context Window (256 Ticks)
플레이어의 행위를 256 개 틱(Tick) 단위의 시퀀스로 묶은 형태이다. 이는
약 수 초간의 연속적인 움직임을 하나의 데이터 포인트로 간주하여,
단발성 조작이 아닌 '흐름'상의 부자연스러움을 포착하기 위함이다. 1 초는
64 개의 틱으로 되어있다. 유저가 킬을 하기전 3. 5 초(2 24 틱), 킬을 한 후
```
0. 5 초(32틱)의 기록을 캡쳐한다.
3.2.2 데이터 규모
795 개의 매치 로그에서 추출된 약 90,000개 이상의 컨텍스트 윈도우를


## 포함하며, 이는 AI 모델이 인간과 기계의 미세한 차이를 학습하기에

## 충분한 양이다.

3.2.3 피처(Features)
총 44 개의 피쳐가 있고 아래는 주요 피쳐를 기입한 표이다.
**# Feature Description**
1 attacker_X X coordinate of the attacking player
2 attacker_Y Y coordinate of the attacking player
3 attacker_Z Z coordinate of the attacking player
4 attacker_vel Velocity of the attacking player
5 attacker_pitch Pitch angle of the attacking player
6 attacker_yaw Yaw angle of the attacking player
7 attacker_pitch_delta Change in pitch angle of the attacking player since
last tick
8 attacker_yaw_delta Change in yaw angle of the attacking player since
last tick
9 attacker_pitch_head_delta Pitch angle distance from the victim's head
10 attacker_yaw_head_delta Yaw angle distance from victim's head
11 attacker_flashed Is the attacker currently flashed
12 attacker_shot Did the attacker shoot their weapon on this
specific tick
13 attacker_kill Did the attacker kill the victim on this specific tick
14 is_kill_headshot Was the kill a headshot
15 is_kill_through_smoke Was the kill through a smoke
16 is_kill_wallbang Was the kill through some wall or surface
17 attacker_midair Did the kill happen while the attacker was midair
18 attacker_weapon_knife Is the attacker holding a knife
19 attacker_weapon_auto_rifle Is the attacker holding an automatic rifle
20 attacker_weapon_semi_rifle Is the attacker holding a semi-automatic rifle
21 attacker_weapon_pistol Is the attacker holding a pistol
22 attacker_weapon_grenade Is the attacker holding a grenade
23 attacker_weapon_smg Is the attacker holding a submachine gun
24 attacker_weapon_shotgun Is the attacker holding a shotgun
25 victim_X X coordinate of the victim player
26 victim_Y Y coordinate of the victim player
27 victim_Z Z coordinate of the victim player
28 victim_health Health of the victim player
29 victim_noise Did the victim player make noise


```
Table 1. major feature
3.2.4 샘플 데이터의 예상되는 문제점
샘플 데이터는 PC FPS(CS2) 기반이므로, 개발 과정에서 이를 안드로이드
TPS 환경에 맞게 최적화 및 재구성 과정이 필요할 수도 있다. 그리고
팀에서 자체 생산할 로그 데이터와 호환이 될 지 확인해봐야 한다. 이
문제는 앞으로 직접 개발하면서 조금 더 고민이 필요한 부분이다.
```
4 예상되는 개선점 및 한계

```
4.1 하드웨어(GPU) 부족 및 처리 지연
딥러닝(CNN, YOLO) 모델과 복잡한 XAI(예: SHAP) 기법은 막대한 GPU
연산력을 요구한다. 이를 수많은 유저가 접속하는 실시간 서버에 적용할 경우,
심각한 시스템 부하와 네트워크 지연)을 유발할 수 있다.
```
```
4.2 양질의 데이터셋 부족
실제 치트 사용자의 데이터를 대규모로 수집하기 어렵고 정상 유저와의 데이터
불균형이 심각하여, 모델이 편향되거나 새로운 핵에 대한 탐지율이 떨어질 수
있다.
```
```
4.3 하이브리드 아키텍처
서버 부하를 막기 위해 연산이 적은 규칙/통계 기반 탐지로 1 차 필터링을 한
뒤, 의심 유저의 데이터만 AI로 분석하는 하이브리드 방식을 채택한다.
```
```
4.4 인간-AI 협업
오탐으로 인한 피해를 막기 위해 AI의 100% 자동 제재보다는, AI가 요약한
시각적/자연어 보고서를 바탕으로 최종 판단은 운영자(GM)가 내리도록
설계하는 시스템적 안전장치가 필요하다.
```

１ Video Games. Anti-cheat in video games: The A to Z. https://irdeto.com/blog/cheating-in-games-everything-you-always-
wanted-to-know-about-it (2022)
２ TiGG, ACE. Defending the Digital Playground: Guide to Game Protection. pp. 26-27 (2025)

３ Nelson Granados. Report: Cheating Is Becoming A Big Problem In Online Gaming.
https://www.forbes.com/sites/nelsongranados/2018/04/30/report-cheating-is-becoming-a-big-problem-in-online-
gaming/?sh=68dfe4077663 (2018)
４ Kapur, S., Singh, Y., Chauhan, V. et al. Hybrid cryptographic and AI frameworks for cheat detection in online games.
Discov Artif Intell. pp. 3 (2026)
５ Thomas, Rylan. The Evolution of Anti-Cheat Systems: A Literature Review of AI-Driven and Behavioral Approaches.
International Journal for Research in Applied Science and Engineering Technology. pp. 977 (2025).
６ Wang, Zilu. New usage of telemetry for anti-cheating in FPS game. Theoretical and Natural Science. 30. (2024).

７ Kanervisto, Anssi & Kinnunen, Tomi & Hautamaki, Ville. GAN-Aimbots: Using Machine Learning for Cheating in First
Person Shooters. IEEE Transactions on Games. pp. 2- 3 (2022).
８ Dan Blechner. Mitigating In-Game Cheating: An Overview of Modern Anti-cheat Strategies.
https://quago.io/blog/mitigating-in-game-cheating-an-overview-of-modern-anti-cheat-strategies/ (2023)
９ Kelly Ma. A New Multi-Tier Anti-Cheat Approach in Online First Person Shooter (FPS) Games. https://nhsjs.com/2025/a-
new-multi-tier-anti-cheat-approach-in-online-first-person-shooter-fps-games/ (2025)
１０ J. Tao et al. "XAI-Driven Explainable Multi-view Game Cheating Detection," 2020 IEEE Conference on Games (CoG). pp.
144 - 151 ( 2020 )
１１ M. M. Z. Loo, G. Luẑkov and P. Burelli. "AntiCheatPT: A Transformer-Based Approach to Cheat Detection in Competitive
Computer Games". 2025 IEEE Conference on Games (CoG). pp. 1- 4 (2025)
１２ 활용 모델: https://huggingface.co/CS2CD/AntiCheatPT_

１３ 활용 데이터셋: https://huggingface.co/datasets/CS2CD/Context_window_


