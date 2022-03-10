
# Mahjong
This is an open source Python libaray of 1-on-1 mahjong game, which provides a standard API to learn algorithms on mahjong environment.
# The game rules
You can see the detailed game rules in appendix of the paper.
# Installation

You can clone the git project, and import the python library,We support python 3.x,and the only requirement is numpy.
```python
git clone https://github.com/yata0/Mahjong.git
```
# API
## Initializing mahjong
```python
from p2_mahjong.wrapper import MJWrapper as Wrapper
wrapper = Wrapper()

```
## Interacting with the Environment
You can see how to use interact with the environment through this example.
```python
import random
from p2_mahjong.wrapper import MJWrapper as Wrapper
wrapper = Wrapper()
is_game_over = False
index = 0
game_count = 100
for game_index in range(game_count):
    is_game_over = False
    wrapper.reset()
    legal_actions = wrapper.get_legal_actions()
    while not is_game_over:
        action_label = random.choice(legal_actions)
        cards, actions, reward, is_game_over, legal_actions = wrapper.step([action_label])
        if is_game_over:
            _, winner_id = wrapper.get_game_status()
            if winner_id is not None:
                print(game_index, wrapper.get_payoffs())
            else:
                print(game_index, "tie")
        index += 1
```
## Tiles and Actions
### <span id="Tiles">Tiles</span>
There are 24 unique tiles and 72 tiles in total in the 1-on-1 Mahjong game, and the relevant tile ids defined in the source code are listed
in the table below.

| Tile name |  ID |
| --- | --- |
| Character 1 | 9 |
| Character 2 | 10 |
| Character 3 | 11 |
| Character 4 | 12 |
| Character 5 | 13 |
| Character 6 | 14 |
| Character 7 |15 |
| Character 8 |16 |
| Character 9 | 17 |
| Green | 27 |
| Red | 28 |
| White | 29 |
| East | 30 |
| West | 31 |
| North | 32 |
| South | 33 |
| Spring | 34 |
| Summer | 35 |
| Autumn | 36 |
| Winter | 37 |
| Mei | 38 |
| Lan | 39 |
| Zhu | 40 |
| Ju | 41 |

### <span id="Actions"> Actions </span>
There are 10 types of actions with 105 different actions in total, and the relevant action ids defined in the source code are listed
in the table below.

|action type |auxiliary tiles|target tile|id|
|---|---|---|---|
|Get Card|-|-|0|
|Hu|-|-|1|
|Discard|-|Character 1<br>Character 2<br>Character 3<br>Character 4<br>Character 5<br>Character 6<br>Character 7<br>Character 8<br>Character 9<br>Green<br>Red<br>White<br>East<br>West<br>North<br>South|12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>30<br>31<br>32<br>33<br>34<br>35<br>36|
|Pong|-|Character 1<br>Character 2<br>Character 3<br>Character 4<br>Character 5<br>Character 6<br>Character 7<br>Character 8<br>Character 9<br>Green<br>Red<br>White<br>East<br>West<br>North<br>South|46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>64<br>65<br>66<br>67<br>68<br>69<br>70|
|Gong|-|Character 1<br>Character 2<br>Character 3<br>Character 4<br>Character 5<br>Character 6<br>Character 7<br>Character 8<br>Character 9<br>Green<br>Red<br>White<br>East<br>West<br>North<br>South|80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>98<br>99<br>100<br>101<br>102<br>103<br>104|
|Chow|Character 2,3<br>Character 1,3<br>Character 1,2<br>Character 3,4<br>Character 2,4<br>Character 2,3<br>Character 4,5<br>Character 3,5<br>Character 3,4<br>Character 5,6<br>Character 4,6<br>Character 4,5<br>Character 6,7<br>Character 5,7<br>Character 5,6<br>Character 7,8<br>Character 6,8<br>Character 6,7<br>Character 8,9<br>Character 7,9<br>Character 7,8|Character 1<br>Character 2<br>Character 3<br>Character 2<br>Character 3<br>Character 4<br>Character 3<br>Character 4<br>Character 5<br>Character 4<br>Character 5<br>Character 6<br>Character 5<br>Character 6<br>Character 7<br>Character 6<br>Character 7<br>Character 8<br>Character 7<br>Character 8<br>Character 9|126<br>127<br>128<br>129<br>130<br>131<br>132<br>133<br>134<br>135<br>136<br>137<br>138<br>139<br>140<br>141<br>142<br>143<br>144<br>145<br>146|
|Concealed Gong|-|Character 1<br>Character 2<br>Character 3<br>Character 4<br>Character 5<br>Character 6<br>Character 7<br>Character 8<br>Character 9<br>Green<br>Red<br>White<br>East<br>West<br>North<br>South|177<br>178<br>179<br>180<br>181<br>182<br>183<br>184<br>185<br>195<br>196<br>197<br>198<br>199<br>200<br>201|
|Pass Hu|-|-|202|
|Ting|-|-|203|
|Add Gong|-|Character 1<br>Character 2<br>Character 3<br>Character 4<br>Character 5<br>Character 6<br>Character 7<br>Character 8<br>Character 9<br>Green<br>Red<br>White<br>East<br>West<br>North<br>South|213<br>214<br>215<br>216<br>217<br>218<br>219<br>220<br>221<br>231<br>232<br>233<br>234<br>235<br>236<br>237|

## Standard methods
### Stepping
	step(self, action: int) -> Tuple[list of list, list of list, list, bool, list]
Run one step of the environment's dynamics.You can call **reset()** to reset the environment's state.This function accepts
an action id and returns a tuple **(tiles, actions, rewards, is_game_over, legal_actions)**
#### Parameters:
- **action**(int):&nbsp; an action provided by the player.This is an integer,and should be one of the **[Actions](#Actions)**


#### Returns
- **tiles**(list of list):&nbsp;one of player's observations of the current environment ,list of tiles,contains player’s hand, the player’s Chow, Pong,
and Kong, the player’s concealed-Kong, the player’s Discard, the opponent’s Chow, Pong, and Kong,
the opponent’s concealed-Kong, and the opponent’s Discard.Each tile in the list is integer, which is one of the **[Tiles](#Tiles)**.
The specific information is shown in the table below:

    | class | description | length | remarks |
    | ------ | ------ | ------ | ------ |
    | self_hand | the player's hand | 34 | complement the length with -1 |
    | self_piles | the player's Chow,Pong and Kong | 34 | complement the length with -1 |
    | self_hidden_piles | the player's concealed-Kong | 34 | complement the length with -1  |
    | self_history_tiles | the player's Discard | 34 | complement the length with -1|
    | opp_piles | the opponent's Chow,Pong and Kong | 34 | complement the length with -1 |
    | opp_hidden_piles | the opponent's concealed-Kong (invisible, replace the real id with 34) | 34 | complement the length with -1 |
    | opp_history_tiles | the opponent's Discard | 34 | complement the length with -1 |
    | last_table_tile | the latest discard tile on the table | 1 | complement the length with -1 |
    | self_flower | player's flower | 8 |complement the length with -1 |
    | opp_flower | opponent's flower | 8 |complement the length with -1 |

- **actions**(list of list):&nbsp;one of player's observations of the current environment, a list of actions, contains player's history actions, the opponent's
history actions,the player's state of Ting and the opponent's state of Ting.The specific information is shown in the table below:

    | class | description | length | remarks |
    | ------ | ------ | ------ | ------ |
    | self_his_actions | the player's history actions | 50 |  complement the length with -1 |
    | opp_his_actions | the opponent's history actions | 50 |  complement the length with -1 |
    | self_wait | the player's state of Ting | 1 | 1 for Ting, 0 for not |
    | opp_wait | the opponent's state of Ting | 1 | 1 for Ting, 0 for not |	

- **rewards**(list):&nbsp;reward returned after previous action, the first item in this list is the reward of player 0, the second item is the reward of player 1.


- **is_game_over**(bool):&nbsp;a signal to check whether the episode has ended.


- **legal_actions**(list):&nbsp; set of legal actions that can be done next step, these actions are also integers.

### Get legal actions
	get_legal_actions(self) -> list

#### Returns
- **legal_actions(list)**

### Resetting
	reset(self) -> Tuple[list of list, list of list, list]
#### Returns
- **tiles**(list of list)
- **actions**(list of list)
- **legal_actions**(list)

#### Current player
	get_current_player(self) -> int
- **current_player**(int):&nbsp;current player to provide an action, which is an integer.

#### Current Observation
	get_current_obs(self) -> Tuple[list of list, list of list]
- **tiles**(list of list)
- **actions**(list of list)

#### Payoffs
    get_payoffs(self) -> Tuple(list, list, list)
- **payoffs**(list):&nbsp;the payoffs of both player, the first is the player 0'score, the second is the player 1's score.
Payoff is same to the reward.


- **<span id="fan_names">fan_names</span>**(list):&nbsp; categories to which the winner's completed legal hand belongs.This is a list of strings.


- **fan_score**(list):&nbsp; list of scores one-to-one  with [fan_names](#fan_names)，which is a list of integers.

#### Game Status
    get_game_status(self) -> Tuple(bool, int)
- **is_over**(bool):&nbsp;a signal to check whether the episode has ended.
- **winner**(int):&nbsp;an integer indicating who is the winner, 0 for player 0 and 1 for player 1.
