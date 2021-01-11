import analyse_box
import json
from ast import literal_eval
from math import log
import operator
import LP_MDS

class compute():
    
    def __init__(self):
        
        self.masks_T = []
        
        self.sbox_threshold = 0.25
        self.LP_threshold = 0.00001
        self.rounds = 4

        #Provide the linear diffusion function 
        self.linear_diffusion_t = None

        #Defines the blockbyte len and the active s-boxes
        self.S = None

        self.blockbyte = None

    def compute_LP_FEISTEL(self,mask,level):
        level -= 1

        if level>=0:
            a = mask>>blockbyte
            b = mask & int('0x' + 'F'*blockbyte,16)

    def compute_LP_SPN(self,mask,level):
        """Recursive function.
           Provided an output mask, computes all the possible input/output masks
           progation that respect the given LP threshold per s-box and total LP threshold. 

           If several masks appear after the linear diffusion, only computes the LP for identical masks.

        """

        #Round counter
        level -= 1

        #Stops when we get to the last round
        if level>=0:
            current_mask = mask[-1][0][0]
            LP = mask[-1][0][1]
    
            #new_masks is the possible
            #new_masks = return_intersection(self.linear_diffusion_t(mask[-1][0][0]),self.threshold,self.S,self.blockbyte)
            
            new_masks = return_best_masks(self.linear_diffusion_t(current_mask),self.sbox_threshold,self.S,self.blockbyte)

            #print(new_masks)
            
            mask[-1] += [(self.linear_diffusion_t(current_mask),1)]
        
            for new_mask in new_masks:
                
                if new_mask:
                    LP = 1
                    x = 0
                    for i in range(self.blockbyte):
                        x<<=8
                        x^= new_mask[i][0]
                        LP*=new_mask[i][1]
                        
                    tmp_masks = mask+[[(x,LP)]]
                    
                    total_LP = 1
                    for x in tmp_masks:
                        for c in x:
                            total_LP *= c[1]
                            
                    #Only continues the procedure if the total LP is
                    #bigger or equal to the specified threshold
                    if total_LP >= self.LP_threshold:
                        self.compute_LP_SPN(tmp_masks,level)
        else:
            
            #print(mask)
            #After a full propagation has been found,
            #computes the total LP of the propagation
            #Adds it to the list of it meets the threshold
            
            total_LP = 1
            for x in mask:
                for c in x:
                    total_LP *= c[1]
            
            if total_LP >= self.LP_threshold:        
                masks = [mask,total_LP]
                self.masks_T += [masks]
                
            
    def create_masks(self):
    
        for j in range(self.blockbyte):
            print('Computing masks for byte ' + '--'*j + '??'+ '--'*(self.blockbyte-j-1))
            for i in range(256):
                i<<=(((self.blockbyte-1)<<3)-(j<<3))
                self.compute_LP_SPN([[(i,1)]],self.rounds)
                
                
            file = 'result_{}.txt'.format(j)
                    
            with open(file,'w') as F:
                F.write(str(self.masks_T))
            self.masks_T = []
            analyse(file,self.S,self.blockbyte)
        

def show(x,counter,blockbyte):
    for i in range(blockbyte):
        print('{:02x} '.format((x>>(((blockbyte-1)<<3)-(i<<3)))&0xFF),end='')
    print(' -> {}'.format(counter))


def choose_LP(masks_OUT):
    """ Provided a list of [[IN,IN,IN,IN],[IN,IN,IN]], returns the masks
        common to all the lists of mask.
    """
    
    x = masks_OUT[0][:]
    for i in range(1,len(masks_OUT)):
        x = list(set(x).intersection(masks_OUT[i]))

    return x
                
def return_intersection(mask,threshold,S,blockbyte):
    """Provided an output mask, returns the best intersection input masks, if they exist"""
    
    L = [(mask>>(((blockbyte-1)<<3)-(i<<3)))&0xFF for i in range(blockbyte)]

    #Returns a list of all mask, per s-box, that meet the threshold
    T = []
    for i in range(blockbyte):
        if L[i] :
            x = analyse_box.targeted_LP_OUT(L[i],S[i],threshold)
            if x not in T:
                T += [x]
    
    #For each active sbox, create a sublist of IN/OUT masks with the given threshold        
    masks_OUT = []
    for mask_list in T:
        tmp = []
        for mask in mask_list:
            tmp += [mask[0][0]]
        masks_OUT += [tmp]
        

    
    if masks_OUT:
        candidats = choose_LP(masks_OUT)
        OUT = []
        for mask in candidats :
            tmp = []
            for i in range(blockbyte):
                if L[i]:
                    tmp += [mask]
                else:
                    tmp += [0]
            OUT += [tmp]
        
        return OUT
    else :
        return []
    
def return_best_masks(mask, threshold, S, blockbyte):
    L = [(mask>>(((blockbyte-1)<<3)-(i<<3)))&0xFF for i in range(blockbyte)]

    T = []
    counter = 0
    for i in range(blockbyte):
        if L[i] :
            x = analyse_box.targeted_LP_OUT(L[i],S[i],threshold)
            if x: counter += 1
            T += [x]
        else:
            T += [[((0,0),1)]]
            
    #print(T)
    if counter : 
        #For each active sbox, create a sublist of IN/OUT masks with the given threshold        
        masks_OUT = []
        for mask_list in T:
            tmp = []
            for mask in mask_list:
                tmp += [(mask[0][0],mask[1])]
            masks_OUT += [tmp]
        #print(masks_OUT)
        T = []
        
        
        for a in masks_OUT[0]:
            for b in masks_OUT[1]:
                for c in masks_OUT[2]:
                    for d in masks_OUT[3]:
                        for e in masks_OUT[4]:
                            for f in masks_OUT[5]:
                                for g in masks_OUT[6]:
                                    for h in masks_OUT[7]:
                                        #for i in masks_OUT[8]:
                                        #    for j in masks_OUT[9]:
                                        #        for k in masks_OUT[10]:
                                        #            for l in masks_OUT[11]:
                                        #                for m in masks_OUT[12]:
                                        #                    for n in masks_OUT[13]:
                                        #                        for o in masks_OUT[14]:
                                        #                            for p in masks_OUT[15]:
                                                                        T += [(a,b,c,d,e,f,g,h)]#,i,j,k,l,m,n,o,p)]
                                                                        #print((a,b,c,d,e,f,g,h))
                                                                    
                
        
        return T
    
    else :
        return []
            
    

def analyse(file,S,blockbyte):
    format_blockbyte = '{:0' + str(blockbyte<<1) +'x}'
    
    with open(file,'r') as F:
        data = F.read()
        
    masks_list = list(literal_eval(data))
    
    print('Computing total LP of each mask')
    
    masks_list = sorted(masks_list,key=lambda tup:tup[1])[::-1]
    #First and last mask
    for i in masks_list[:12]:
        print('IN : ' + format_blockbyte.format(i[0][0][0][0]) + ' OUT : ' + format_blockbyte.format(i[0][-1][0][0]) + ' -> {}'.format(i[1]))

    #Intermediate masks
    for masks in masks_list[:12]:
        mask = masks[0]
        print()
        for i in range(len(mask)-1):
            if len(mask[i])>1 and i<len(mask):
                IN = mask[i][0]
                OUT0 = mask[i][1]
                OUT1 = mask[i+1][0]

                print('OUT : ' + format_blockbyte.format(IN[0])   + ' -> {}'.format(1))
                print('MDS : ' + format_blockbyte.format(OUT0[0]) + ' -> {}'.format(OUT0[1]))
                print('Sbox: ' + format_blockbyte.format(OUT1[0]) + ' -> {}'.format(OUT1[1]))
                print()
        print('Total LP : {}'.format(masks[1]))
        print()
        
            

