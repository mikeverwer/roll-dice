#!/usr/bin/env python
import PySimpleGUI as sg
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
# required files
import make_window as make
from classes import mainframe
from classes import simulation
from classes import roll

matplotlib.use('TkAgg')

# ----------------------------------------------------------------------------------------------------------------------
# Image Data
# ----------------------------------------------------------------------------------------------------------------------

images = {
    'die1': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAF+SURBVEiJ5ZWxTgIxHMY/Lxa5jXYhLPSGm9W43wOQ3jEdD8BkiJPxNYwPwQwMkBv1FUx8AjmTa12OY6ECSesiDi42gomJv7X//Pq1+ZL/ET4ghFxwzm8ppW3f9088z4MrxhhordeLxSKfz+c32+328fOQc37V7XZflVJ2H6SUNo5jFQTB4DNxkiTKGLOXeIcxxsZxrAgh5wjD8GHfxF8pisKGYXjvUUp5s9l0/l8XWq0WGo0G9+r1eu2g5g983z9xr8QP+Afy2WyGfr+PLMvc7VEUvXxXrel0ahljFoBljNksy76tYxRFL07JJ5MJyrIEAJRlidFo5BTcSZ6mKRhjAADGGHq9npP82GVICIHhcIjxeIw0TdHpdA4n310ghHAdB/BXqvj35Frr9W+ItdZrr6qquVLqoGIpJZbL5TMIIeeH3kRCCFWr1U4BAEEQDJIkUVLKvcRFUVghhGq325cAcLR7CiHkjHN+RynlP9n+q9XqraqqPM/z681m8wQA774nKEMISi18AAAAAElFTkSuQmCC',
    'die2': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAG9SURBVEiJ7VW9btpQGD2xdAkejTcPXA9mTaMKxotkVttsvAJV1KnKA4DEAEPVF2AHBh6hqYSQ50pdKQNGsp0BwcQtf74dErukWZCdMWc9V+f7ud93vis8gxDykVL6VVGUoizL15Ik4VJEUQTO+W69XnuLxeL+cDj8TEhK6ed6vf4YhqHIgiAIhG3boa7rd0nGjuOEURRlEo4RRZGwbTskhNzCMIwf5xnPZjPR7XaF67qpA/i+LwzDeEClUpmfC2uaJgAIVVXFYDBIHaBcLv+W8vl8Lu79eDyG7/sAgNVqhX6/f/Gn/g9Zlq9fjES1WoWqqjGJWq2WWhwAwBhbnpczHA6FaZqi0+mI4/GYui2MseUr8bcCY2x5+aakwLv4u/g/nE4ntNttmKaJ0Wj0+kGWOW+1WkKW5cSLzs0u85xPJhNwzgE8edF0On3BS5zzXVrxZrOJQqEAANA0DY1GI+E45zsYhvEQBEHqNXddV/R6PTGfJ84tfN8XpVLpOwght299iSzLCnO53A0AQNf1O8dxwiwVxBlblhUWi8VPAHAV94gQ8oFS+k1RFJrm+m+32z+bzcbzPO/Lfr//BQB/ATmrZWX1MPnyAAAAAElFTkSuQmCC',
    'die3': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIaSURBVEiJrVU9j9pAFJxDWQ6XXjoX2IVpk1MEpZFMh2yozA+gITqlivIDQKKAIsofoKMACqAA0eUiIUR9UlpCAUjGKfiocODAmyIBQe4iOYZp39O82dnZtzf4A0LIW1EUP/E8H+I47tbn88EtHMeBbdub5XI5GY/HH5+enh6PRVEU36dSqR+WZbFLMJvNmK7rliRJ90fFyWTSchznIuIDHMdhuq5bhJA7yLL89VTxcDhkxWKRDQYDzwNM02SyLD8gGo2OTokFQWAAWDAYZNVq1fOASCTy3RcIBPwH7xuNBkzTBADM53OUy2XXl/o3OI67PYtELBZDMBg8FBGPxz2TAwAURZmeHqdWqzFVVVmhUGC73c6zLYqiTJ+RXwuKokxdv5ROp4NMJoNut+vdlpfQbrcZpZQBYJRS1u12r6e81WphsVgAABaLBRqNhivhrsgNwwClFABAKUU6nXZF/spNk6ZpqFQqaDabMAwDiUTieuSHAZqmuW0H4NKWf2G/3yOfz0NVVdTr9ecNl+Q8l8sxjuOOu+h02f1Xzl9Cr9eDbdsAfu+ifr9/VvfZtr3xSp7NZo8pEgThLEW2bW8gy/LDbDbz6gwbDAasVCqx0ei4uZlpmiwcDn8BIeTu2j+RpmmW3+9/DQCQJOk+mUxal5zgoFjTNCsUCr0DgJuDR4SQN6IofuZ5XvTy+6/X65+r1WoymUw+bLfbbwDwCxlCy8JiS1i/AAAAAElFTkSuQmCC',
    'die4': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIzSURBVEiJ7VW7jtpQED2LZHZNB+4osAvTJqvIlEYyLY/fiFaponwAyBS4iPIDUPIq+IRsEMKIMtK2mAKQLk7BozIJD0+KBAsvkoXYraKccmbuuTNzZ869wV9wHPdOFMXP0Wg0wfP8bSgUwqVwXRebzebXarWaTiaTT7vd7rvnFEXxQ6FQ+GHbNr0E8/mccrmcLUnSg5dxPp+3Xdd9EfERrutSLpezOY67hyzL304zHo1GVKlUaDAYXERmmiZVKhWyLMuzMcZIluVHpFKp8SlxPB4nACQIAjWbzUDier1OsViMAFA8HvddoCiKFbq7uwsfe9/pdMAYAwAsFgtUq9XAh6zValgulwAAxhg6nY7n43n+1jcS6XQagiAcnchkMoHkmUwGkUgEACAIAtLptD9AVdXZaamtVos0TaNyuUz7/T6wLfv9nnRdJ03TqN1u+3yqqs7OyF8LqqrOLt+UK/Cf/F8nbzQa0DQNuq7jcDgEHj4cDiiVStA0De12+zzgdM5N0/S0IhKJkK7rgbNcLBaJ53lPi07F7mzOTdP0tMJxHHS73cDMe70eNpsNgD9a1O/3/QGKonhSZlmWTxWfr/RzNJtNnyqOx57AkqIoFmRZfpzP557RsiwyDIOGw+FFaz4YDMgwDB8xY4ySyeRXcBx3/9o/UTabtcPh8BsAgCRJD/l83j6t4BowxiibzdqJROI9ANwce89x3FtRFL9Eo1Hxmt/fcZyf6/V6Op1OP2632ycA+A36gJvsW+G55QAAAABJRU5ErkJggg==',
    'die5': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKSSURBVEiJrVU9b9pQFD1BNcFs2BsDZnDWNqqc0UhmiwxM5AdkqqJOVX9AImeAoeofSKaIrwEyJGJLihBGGSt1jTOESA93CDBBm4BvhxYLh8i1Es747n3n3Xffueet4R84jnsvSdKXWCyW4Hl+PRQKISgcx8FkMvk9HA57t7e3nx8fH7+7QUmSPuZyuZ+2bdNr0O/3KZPJ2Mlkcs+tOJvN2o7jvIp4DsdxKJPJ2BzHbUKW5W+LFV9fX1OhUKButxuIzDRNKhQKZFmWu8YYI1mWL7G1tXWzSByPxwkAiaJIlUrFl7hUKpEgCASA4vG45wBFUaxQJBIJz3tfr9fBGAMA3N/f4+joyPchj4+PMRgMAACMMdTrdTfG8/y6RxKpVAqiKM6DSKfTvuTpdBrRaBQAIIoiUqmUN0FV1bvFq1arVdI0jQ4PD2k6nfq2ZTqdkmEYpGka1Wo1T0xV1bsl8lVBVdW7wJNyfn6O3d1dNJvNoFuW2/Iczs7OXFUIgkDNZnN1lZ+enrqqGAwGHlX4IRB5Pp+HIAgAAEEQsLOzE4j8TZAkXddxcnKCRqOBfD6P7e3t1ZHPD9B1PWg6gGfaUi6XoWkaDMPAbDbz3TybzXBwcABN01Cr1ZYTFtVimqarimg0SoZh+Cpif3+feJ53vWjR7JbUYpqmq4rxeIxWq+VbebvdxmQyAfDXizqdjjdBURTXyizL8rji05F+ikql4nHFmxvXYElRFAuyLF/2+3130bIsKhaLdHV19d9BISLqdrtULBY9xIwx2tjYuADHcZur/ol0XbfD4fBbAEAymdzLZrP24g1eAsYY6bpuJxKJDwCwNu89x3HvJEn6GovFpJf8/uPx+NdoNOr1er1PDw8PPwDgD9oXAlg17L5iAAAAAElFTkSuQmCC',
    'die6': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALOSURBVEiJvVU9T9tQFD1EcsAZjIIlI2XAGczaosqMjuSMxGGAX2CWCnWq+gNAZkiGqhJihDEOGSLYYClFgC3GQlfMQJAcg8SHMiQtJL4daKyYCBdB1TO+e3Xeeee9e94A/oBhmHeiKH5OJpNjLMsOxmIxPBe+76PVav26ubmpnZ2dfbq/v/8eFEVR/DA9PX3heR69BvV6nTRN89Lp9HygOJ/Pe77vv4q4C9/3SdM0j2GYCUiS9K1X8cnJCRUKBbJt+1lklmVRoVAgx3GCNdd1SZKkHUxOTp72EqdSKQJAPM9TuVyOJC6VSjQyMkIAKJVKhTaQZdmJDQ0NxbveV6tVuK4LALi6usLq6mrkRa6treH6+hoA4LouqtVqUGNZdjD0JDKZDHie7xaRzWYjybPZLBKJBACA53lkMplwg6Io571HXV9fJ1VVaWlpidrtdqQt7XabDMMgVVWpUqmEaoqinPeR/ysoinLeNyn7+/vQdR2maUZa0kWpVMLc3Bxs2+4v9io/OjoiQRAIAHEcRysrK5HqlpeXieM4AkCjo6N0fHz8tPLt7W1cXl4CABqNBjY2NiJVb25uotFoAAAuLi6wtbUVqofIp6amIAgCAGB4eBizs7OR5DMzM+A4DgAgCAI0TXvaFqKHidN1/a8D1IVpmqTret9E///XYpomVFWFYRjodDqRtnQ6HSwuLkJVVVQqlf6GXuWWZQVZkUgkyDCMSHULCwvEsmyQRb3W9Cm3LCvIimazid3d3Ujle3t7aLVaAB6y6ODgINwgy3IQZY7jhFLx8Ug/RrlcDqXi6WkQsCTLsgNJknbq9Xqw6DgOFYtFOjw8fNbF2bZNxWIxROy6Lo2Pj38FwzAT//onyuVyXjwefwMASKfT8/l83us9wUvgui7lcjlvbGzsPQAMdL1nGOatKIpfksmk+JLfv9ls/ry9va3VarWPd3d3PwDgN0sYp3npWVpUAAAAAElFTkSuQmCC',
    'lock1': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGySURBVEiJ5dVPSxtBGMfx38xmsp0lRhOKRQ8NaGv2kFUQX0QvPYhVtFLsvafq3dJ76bVXD4qrMeLJV6EWmoSsovjnoC60aHbb3WzGzfSiPZQWts0Kgt/zw2eGYeAhuM5kbDjoTH8IOX8sGVMlIYgakRJEiID6/olad+amhPgMAAQAFjLpN6Knd/7yxWh3mEpFRn+Pui6ypQ07cXb2/vVF/RMxGRv+/vTJ5teZ6Uf4h9v+NSnxcGHR5vsHz5Tn2czSt5npglTV9mEAIARBf19KrVQHaMh5rp2n+FNhugN4wHNUJpRkrPJ1Laao9Dbgm+4BXqtZKK6WYFm78eK1moXiyhq2t3awahaxa+3Fh1fKVXieDwDwPB/lciU+3BgsQNM4AEDTNBhGIRKeiDKk63lMTI6jUq7CMArI6wPx4TcH6Ho+6jiAu/IV7x5ORRjcCizCgNKGf0xdN1ZYcVyQhn9EE3VnLlPasCFlPLKU6Cqt20nHnVXWW63zsSvxQz04HAn6+1LtbCTFcZFdNu3kqf3uledt/lqaJmNDfmf6o+Q891/bvykapOGfqI779mWz+QUAfgIkIqKOOyIlKAAAAABJRU5ErkJggg==',
    'lock2': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIaSURBVEiJ7ZUxaBNhFMf/312+nheTS3KKokOOJqlTmgulEjd1EQdLLbpolbg7ibviLq5FcAhiMYviVFzaKi6mFYRaN5OcHUwCHto7vcvl8+4cTGK1iL2kY3/b997Hj8fj8R5BlzKlE05MuuuKYtKnVPAJwU4hvg/CmMPZ9oawady8xNhbACAAUEpI19mRo7e+Xpw55EYiO5b+DWeakJ88a4UajTvXvmzOkTKlE9/GMgufi7OHEaDaf+L7OFh61BI/VM/yU3JiXi/OZn1BAADouo6VyioIxyEejwWXEwInnYoI6++PhVxRVHqt0HUd9+cewDAMhMNhTJ8/BzWvBva7UhTYJyqcH+JHesF3a+swDAMAYFkWVipvglfexaO8wG0NjKZGEQ6HAQCUUqQzqYHlABDa+lCUJKZnplB5vYpMJoVTp0/unhwAVDUHVc0NJe3B/f/LnnxP3mXbKAbB8zwsLS6jVtNQOHF82wgPJV9aXMbLF6/AGEOz0UQ8HoeiJPv5odpSq2lgjAH4tYu0uvZHnuOY6wwqLxQm+7tIkiSM57K/xcx1Qlzb/siZZtqLRgPL1byKeCIBra5hPJeFLMsAAN4wQdq2RuYpzVtj6ed68cquXaIDpYet/VXtDP/U85oXfrDvQrU+6aRTkd5FGgTeMCE/LrdGPrVuX7WshX6pZUpVOybd80VRGej6d1ibtO0NwTBvXO501gDgJ7gmwQA4AZCHAAAAAElFTkSuQmCC',
    'lock3': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJ5SURBVEiJrZVNTBNBFMf/s+2w7lqWthqNHtjQFuih2yUEgzf1YjxIkPgRFQ3ePRnvGu/GKzHxQIzECmI8ES+Axot8qAktaTFSVg5CEzfKru62jN31AEUUjG3p7zZvJr95mXl5j2CDBKXthQbpblEQGl1KeZcQlAtxXRDGCpxtL/Grxs1LjL0HAAIAAwHpOjt0+Na3cz0Hij5f2dK/4UwTwZHnOe/y8p1rX1f7SYLS9u/NkdEvfb0HUUG2/8R1sX/gUU74uHDK0xUMDOp9vTGX5wEAuq5janIahOPg9zdULicEhXDIx6fmWrxFQZBLT6HrOu73P4BhGBBFEd1nTkNtUyv2F6V6YI8gc67XU1cKJmdTMAwDAGBZFqYmZyrPfAOHenhua6Ap1ARRFAEAlFKEI6Gq5QDg3bqQ5UZ093Rh8s00IpEQjp84Vjs5AKhqHKoa35W0BPf/I+uk0xkMD40gk5mvrTydzmD4yVO8nXmHocQw5jMfaidPJedgWTYAwLJsJJOp2smVeAyiKAAARFGEosTKkm/70J2IRltx4eJ5pJJzUJQYWqMttZOXLohGW8s9Xpl8JxzHwfjYBLJZDZ1Hj2wr4V3Jx8cm8OrlazDGsLK8Ar/fD1lu3Nwvu853IpvVwBgDsN6LtEXtj32OY8VCtfLOzo7NXiRJEpT47yriWLHg5fL2J840w059fcVytU2FPxCAtqhBiccQDAYBAB7DBMnbGhmktM1qDr/Q+67UbBLtG3iY27ugnfQ8c5yVsz/ZD35hsaMQDvlKE6kaPIaJ4ONEru5z7vZVyxrdTDVBqWo3SPdcQZCrmv5rLE/y9hJvmDcur63NAsAvPAPlbZ7mN2kAAAAASUVORK5CYII=',
    'lock4': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALISURBVEiJ7ZVBaFN3HMc/7yV/43trX9NEHA7W8JJ2p7SvFNf2VrPI2EHRohetUi9FZKexu2P3sasIHooo68UxRWQX7WRM2lRptPHWpC8t2AYM2pftpel/yfOgyay1WS2exO/tx/fP5//7//nx/Sm80oQQfZU246eqpnV4QgQ8RWG7UjwPRcqKWi4vBlad709IOQugAIy3G9/KfZ+df358eG+1pWXb0DellkqErv1W8C8v/3jm2eoFZUKIvr+7Om89HR35lHfodkt5HnvGrxS0+ew3vsOh9qvF0ZG4FwgAUCwWSU3PoKgqwWDb/7Lydp707ENaDQNd10BRqMSiLYHM4y/8VU2L1L+iWCxy8cIlHMdB13WOHD2E1WttCU7Pprlx/SauW+beX1OcPTdGOByiarTCbi2ien7frvrhuUcZHMcBwHVdUtP3m3adSj3AdcsAOI5DZi7T8GrCF1BfP2xGTXRdB0AIQawz2hQei0URQgCg6zqmaW7w/a8XkUgHR4YPMz01Q2dnlAOJoabwxFdDoEB2PsfgYD8dkc+3hgNYVg+W1dMUWpeqqiSTCZLJxNv9bVF2qI/wDwy+aRTTs2lSqQfEoiaJ5AFUdev7a7Uad25PksvZDAx+uWmEN8Dzdr6RFUuLS6AoJA++fYYB7tye5O4ffyKlZGV5hWAwSCTS0fA3tGXb+UZWSCnJZXNNn53L2UgpgZdZZC/YG3xVldVKvYh3xzEMA3iZFQOD/U3hAwP7G1lkGAbdPfH/wLJa8atr5bxaKsVqra2EwyHOnhsjM5fBNM1NWfGmrF6LYHs79oJNd0+cUCgEgM8poayVbeWqEL1uV+z34uip97aJwuOXC59k7a99v9ZqK8f+lf8Esgv7K7FoS30j7UQ+p0Tol4nCrieFH0677q1GqxNCWOU242dP0yI72v7rck1ZKy8GnNJ3J9fXHwG8AJ/gBT4wSut6AAAAAElFTkSuQmCC',
    'lock5': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMjSURBVEiJrZVBbBtFFIa/XXtrdkk2jo1AIBFr7bTxwfZGVWlya40R4kBVKqACShUuVVX1hLgXcUdcKyQOEaLCNBQBQhWXtiAEatyGmNpRXFQ761QisVQLuqbrOFN7OQSbpEmMKflvo/fm2zcz/74n8bfSirK3MaC/31TVIVdRfK4k0ask10USoiHX64u+u/Y7rwsxCyABTA7qp8WTT53545Ujjzf7+nqGPii5ViNw4cuKd2npvbd+v3tWSivK3j93D1+8M3HsCf5DtdvKdXls8pOKeqv4gudQYPBcdeJYzPX5AKhWq2SmryHJMn7/wL+yylaZ7Owv9Os6mqaCJNGIhPt8+bk93qaqhtpXUa1W+fDsR9i2jaZpHH7pRcxRc1twdjbL1199g+PU+enHq5w8dYJgMEBT74dH1JDsej272sm5G3ls2wbAcRwy09e7Vp3JzOA4dQBs2yafy3diLcXjk9cnG2EDTdMAUBSFyHC4KzwSCaMoCgCapmEYxoa4d/0iFBri8JFDTF+9xvBwmIPJA13hyWcPgATFWyXGx/czFHp6eziAaSYwzURXaFuyLJNKJUmlklvHe6IA8/MFps5foFC42euW3uDz8wWmPvucmes/cz49xc3CrzsHz+fmOq5wnDq5da743/B4Irb2g7Dming81hN804NupWh0hKOvvUo+N0c8HmMkumfn4O0PRKMjvaZvDc/OZslkZoiEDZKpg8jy9jfXarW4fOkKpZLF2Pgzmyy8AV62yp1ecXvxNkgSqee29jDA5UtX+P67HxBCsLy0jN/vJxQa6sQ3lGVZ5Y4rhBCUiqWuxy6VLIQQwFovshasDXFZFs1GexGLx9B1HVhzxdj4/q7wsbF9nV6k6zrxxD8ukkWz4ZVX6mW5Vou0+vsJBgOcPHWCfC6PYRibesWDMkdN/IODWAsW8USMQCAAgMeuIa3ULemcoow6uyPfVife3LFJFJz8uPJo0Xre80WrtfzyfXHPV1zY14iE+9oT6WHksWsEPk1Xdv1Wefe441zslJpWFLM+oH/gqmrooab/qliRVuqLPrv29hurqzcA/gIjvSmrbKxhRgAAAABJRU5ErkJggg==',
    'lock6': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOISURBVEiJrZVRTBt1HMc/d+VWepSjFCNgIre24LZAuWZhwNzDhjXGB5e56IviRGPIsvhkfNf4bnxdTHwgZmRkilFjFqNu0+h0KyPtRklg0nJlyYDERnctvStnWx+QSoFWXPy+/e/7z+e++f9//99P4G9NSNLhfJPyfsHl6ihJkrMkCOxVQqmEYNt50TSXnA+Mt1+y7SiAADDWrLxptz/2zh8vnn604HbvGbpdYiaDd/Lz1brl5fde+/3BeWFCkg5nuzov/zYy3Mp/SFtVpRKPjF1YdS0knnWc9DaPp0eGe0pOJwDpdJrIzSkEUcTjafpXVkpPEYveplFRkGUXCAL5gN/tjM8+UVdwudTNo0in03x4/iMMw0CWZU49/xxaSKsKjkVjfPnFV+RyJj9fv8HZc6O0tHgpKI1Q71LFUp1j3+bmmTtxDMMAIJfLEbl5q2bqSGSaXM4EwDAM4jPxsleUHE5x62af34csywBIkkSg018THgj4kSQJAFmW8fl8FX7d1oWqdnDq9Elu3piis9PPiaHjNeFDTx0HARILSQYH++lQH68OB9C0XjSttyZ0U6IoEg4PEQ4P7e5v/7CYXOSTS5PEorf39INoNManlyZJ6akdXkXy5fvLjF+4SDa7Rjw+i2maHH1ysCr4+k+/8O0332FZFnNzd3lj9HXa29t2Tz4/f5dsdg2AvJVnZma2ZurZ+CyWZQGQzWaZn5uv8CvgBw4ewO1uAKC+vp5gsLsmvDvYjbN+4/G53W4OHTpY4VccS3t7G2deHWZqapqurk60UO2LPXbsKA0NMgu/JjjS30drW2t1OIC6X0Xdr9aEblUopBGq8op3wGPRGJHINAG/j6HwCURxR0GVVSwWuXrlGsmkzsDgkR0lXAFP6alyr7i3dA8EgfDTu9cwwNUr1/jh+x+xbZuV5RU8Hg+q2lH2K2LpeqrcK2zbJplIVgUDJJM6tm0DG71IX9QrfFG0C/nNRU+wB0VRgI1eMTDYXxM+MNBX7kWKohDs7fkHbBfydaJlpsRMJlBsbKSlxcvZc6PEZ+L4fL4dvWK7tJCGp7kZfVEn2NuD1+sFwGFkECxTF8YlKZTrCnydHnnlf5tELWMfrzYk9GccnxWLKy/8aa85E4t9+YDfvTmRHkYOI4P34sTqvvur757J5S6Xo05IkmY2KR+UXC71oab/um0JlrnkNDJvvby+fgfgLxhlT0CvnDboAAAAAElFTkSuQmCC',
    'down': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAKCAYAAABfYsXlAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD6SURBVCiRtZLBSkJBFIa/40x3sH0ubGuQ1VtEbao3iFpGCdZbRCBEb2D5BhVCl3yM3Nrqgrdtone4dFpIodaNm+C3m5l/vjM/jISdtrIgCsCi5GonV0ni6b500TnmCcLm1gZBEHzvTcmdGx9cN27o92OcCzDGkoX3njRNqaxVqJ/XpsQAEnbaH4DMNrhrtni4fyRJPKo/mzjnsEuW07MTdna3EZHZiP4q/6LXe+XqskEURYyGIwCMMVhr2D/Y4+j4kOJyMavY33IAVSV8eua22WLwPqBaXad+UaO8Ws66kl8+SRy/USqt5IkCaCFvEviPGBj/81yvngP5BK0MVHD9uAUFAAAAAElFTkSuQmCC',
    'up': b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAKCAYAAABfYsXlAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD6SURBVCiRtdFBSgMxFMbxfyZxQj1C3Vbs7KpXEN2oNxBdii20Ct5BkCIewaonUCky0iuoJ6g7S8etZZowGHeFYRrKgP2WL8kvj/dEPOg7lpQAWBbugjK3k+S7lK4Wfu8c8csrvd4Dk58JUVSnfdaiulZdiIt40P8FxLzD4fCTq8suX6MR03QKgJQSpST7B3scHR9SWa14+5qLG2O5u73n6fEZYyzOFdeitUatKE6bJ+zsbiNEob8i/v72wXX3hvE4QesQKf2Ts9aSZRm19RrtTot6tJHDcy+NsQCcX3S8oC9pmmKtJQzDWS2Hax2yudUoDfsS4FnmP0T8AVnYVU+ZVHgeAAAAAElFTkSuQmCC' 
}
# ----------------------------------------------------------------------------------------------------------------------
# Functions for calculations
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Making plots
# ----------------------------------------------------------------------------------------------------------------------

def create_histogram(outcomes, die_rolled, trials):
    if (0.015 * die_rolled) < 0.99:
        width = 1 - 0.015 * die_rolled
    else:
        width = 0.99

    plt.hist(outcomes, bins=range(1, max(outcomes) + 1), align='left', rwidth=width)
    plt.xlabel('Sum of Dice Rolled')
    plt.ylabel('Frequency of Sum')
    plt.title(f'Results of Simulation: Rolling {die_rolled} Dice, {trials} Times')
    plt.xlim(die_rolled - 1, 6 * die_rolled + 1)


def create_convoluted_distribution_plot(distribution, number_of_dice, mean, deviation):
    # all possible outcomes
    outcomes = list(range(number_of_dice, 6 * number_of_dice + 1))  

    if (0.015 * number_of_dice) < 0.99:
        width = 1 - 0.015 * number_of_dice
    else:
        width = 0.99

    plt.bar(outcomes, distribution, width=width, align='center')
    plt.xlabel(f'Sum of {number_of_dice} Dice')
    plt.ylabel('Probability')
    plt.title(f'Probability Distribution of the Sum of {number_of_dice} Dice')
    plt.ylim(0, max(distribution) + 0.2 * max(distribution))

    # Draw vertical line at the mean
    plt.axvline(x=mean, color='r', label="mu")
    plt.annotate(fr"    $\mu$ = {mean:.2f}", xy=(mean, max(distribution) + 0.1 * max(distribution)),
                 xytext=(mean, max(distribution) + 0.1 * max(distribution)), ha='center', va='bottom')

    # Draw vertical lines 1 standard deviation from the mean
    plt.axvline(x=mean + deviation, color='g')
    plt.axvline(x=mean - deviation, color='g')
    plt.annotate(fr"    $\sigma$ = {deviation:.2f}",
                 xy=(mean + deviation, max(distribution) + 0.05 * max(distribution)),
                 xytext=(mean + deviation, max(distribution) + 0.05 * max(distribution)), ha='left', va='bottom')


# ----------------------------------------------------------------------------------------------------------------------
# Matlab helper code for GUI
# ----------------------------------------------------------------------------------------------------------------------

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=0)
    return figure_canvas_agg


def clear_canvas(canvas_agg):
    canvas_agg.get_tk_widget().destroy()  # Destroy the existing canvas
    plt.close()


"""
# ----------------------------------------------------------------------------------------------------------------------
    Beginning of GUI Code
# ----------------------------------------------------------------------------------------------------------------------
"""


def main():
    # ---------------------------------------------------------------------------------------------------------------------
    # Initialize Window
    # ---------------------------------------------------------------------------------------------------------------------
    sg.theme('Default1')
    mf = mainframe(images)  # MainFrame object, see classes.py
    window = make.mainframe(sg, images, theme='Default1', frame=mf)
    mf.window = window

    fig_canvas_matlab_convolve = None
    fig_canvas_agg_simulated = None
    dice = 3
    selelect_box_id = None

    # ----------------------------------------------------------------------------------------------------------------------
    # Event Loop
    # ----------------------------------------------------------------------------------------------------------------------

    while True:
        event, mf.values = mf.window.read(timeout = 1000 // mf.update_interval)
        sim_graph = mf.window['simulation graph']

        if event in (None, 'Exit'):
            break

        elif event == 'About':
            mf.window['log'].update(value='')
            print('Created by: \nMike Verwer; M.Sc. Mathematics, McMaster University.\n2023\n',
                  '\nMade in Python with the PySimpleGUI library and matplotlib.\n',
                  '\nIntended for use in Math 10064 @ Mohawk College')

        elif event == 'The CLT':
            mf.window['log'].update(value='')
            print('Suppose you are running an experiment in which the outcomes have an arbitrary probability '
                  'distribution (just like the dice in this program).\n',
                  '\nSimply put, the Central Limit Theorem says that if you run this experiment \'N\' times, then'
                  ' the sum of those N outcomes will be normally distributed, as long as N is large enough.\n',
                  '\nTest it out by making a very skewed die distribution and setting the number of dice (our \'N\') to'
                  ' be small. Press \'Show Sum Distribution\' to see how likely each possible sum is. As you increase N'
                  ', the resulting graph should look more and more \"Normal\" shaped.')

        elif event == 'SaveSettings':
            filename = sg.popup_get_file('Save Settings', save_as=True, no_window=True)
            mf.window.SaveToDisk(filename)
            # save(values)
        elif event == 'LoadSettings':
            filename = sg.popup_get_file('Load Settings', no_window=True)
            mf.window.LoadFromDisk(filename)
            # load(form)

        elif event.startswith('face'):
            active_face = int(event[-1])
            mf.activate_slider(event=event)

        elif event.startswith('lock'):
            active_lock = int(event[-1])
            mf.activate_lock(active_lock)

        elif event == 'preset':
            set_to_preset = mf.values[event]
            mf.set_sliders_to(mf.presets[set_to_preset], reset_locks=True)


        elif event == 'add preset' and mf.values['preset'] != '':
            mf.add_preset(mf.values['preset'])

        elif event.startswith('input'):
            active_face = int(event[-1])
            previous_values = [mf.values[f'face{i}'] for i in range(1, 7)]
            input_value = mf.values[event][:-1]
            try:
                active_face_value = float(input_value)
                mf.activate_slider(f'face{active_face}', mf.values, active_face_value)
            except ValueError:
                if mf.values[event] != '':
                    sg.popup('Enter a number', title='Error')
                elif mf.values[event] == '':
                    mf.set_sliders_to(previous_values)

        elif event == 'Randomize':
            if False in mf.locks:  # At least 1 slider is unlocked
                mf.die_distribution = mf.random_distribution(get_var=True)
                mf.set_sliders_to(mf.die_distribution)

            mf.die_distribution = [mf.values[f'face{i}'] for i in range(1, 7)]
            mf.mean_and_deviation(update=True)

        elif event == 'up' or event == 'down':
            if event == 'up':
                new_dice = int(mf.values['dice']) + 1
                mf.values['dice'] = new_dice
                mf.window['dice'].update(value=new_dice)
            else:
                new_dice = int(mf.values['dice']) - 1 if int(mf.values['dice']) > 1 else 1
                mf.values['dice'] = new_dice
                mf.window['dice'].update(value=new_dice)

        elif event == 'theory_button':  # Make the theoretical distribution plot
            # Get the number of dice to roll
            try:
                previous_distribution = mf.die_distribution
                previous_dice = dice
                dice = int(mf.values['dice'])

                # Convolve the single die distribution with itself 'dice' times
                # to find the probability distribution of rolling all the desired dice
                convoluted_distribution = mf.die_distribution
                for _ in range(dice - 1):
                    convoluted_distribution = np.convolve(convoluted_distribution, mf.die_distribution)

                # Create plot of theoretical distribution
                plt.figure(figsize=(10, 4))
                # create_dice_distribution_plot(die_distribution, face_totals, die_mean, die_standard_deviation)
                mf.window['log'].update(value="")
                conv_mean, conv_deviation = mf.mean_and_deviation(distribution=convoluted_distribution, update=False, dice=dice)
                create_convoluted_distribution_plot(distribution=convoluted_distribution, number_of_dice=dice, mean=conv_mean,
                                                    deviation=conv_deviation)
                fig = plt.gcf()

                # Draw the plot if related inputs changed
                if mf.die_distribution != previous_distribution or dice != previous_dice:
                    if fig_canvas_matlab_convolve is not None:
                        clear_canvas(fig_canvas_matlab_convolve)
                    fig_canvas_matlab_convolve = draw_figure(mf.window['canvas'].TKCanvas, fig)

            except ValueError as ve:
                sg.Popup(f'Value Error: {ve}')

        elif event == 'go':  # Run the show
            # Get the number of dice to roll and rolls to perform
            try:
                # Run the simulation
                mf.simulate = True
                mf.window['simulation graph'].erase()
                sim = simulation(mf)

            except ValueError as ve:
                sg.Popup(f'Value Error: {ve}')
        
        elif event == 'simulation graph':
            print(f"[LOG] pressed {event}: {mf.values[event]}")
            if selelect_box_id:
                sim_graph.delete_figure(selelect_box_id)
                selelect_box_id = None
            click = mf.values[event]
            found = False
            for roll_obj in sim.rolls:
                if not found:
                    if roll_obj.is_hit(click):
                        found = True
                        selelect_box_id = sim_graph.draw_rectangle(roll_obj.hitbox[0], roll_obj.hitbox[1], 'magenta')
                        print(f'hit roll {roll_obj.roll_number}')

        
        ######################################
        # Animation
        ######################################
        if mf.simulate:
            if sim.trial_number <= sim.number_of_rolls:
                print(sim.trial_number)
                sim.roll_dice(sim.trial_number)
                sim.trial_number += 1
            else:
                mf.simulate = False

    mf.window.close()


if __name__ == '__main__':
    main()
