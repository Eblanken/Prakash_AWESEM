# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 23:10:21 2018

@author: Erick Blankenberg
"""

import mpipe

def doNothing(task):
    print("Am Alive")
    return 1
    
stage1 = mpipe.OrderedStage(doNothing, 3)

pipe = mpipe.Pipeline(stage1)

pipe.put(1)

result = pipe.get()
print("Alive!!!")