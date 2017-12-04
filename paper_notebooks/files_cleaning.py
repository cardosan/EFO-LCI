
# coding: utf-8

import pandas as pd
import numpy as np

##################################GENERAL############################################

def import_general_file(one,two,three,four,eco,man_c,sp_c):
    """function that import the file with the general infos, combine them making some cleaning"""
    #remove empty rows
    one=one.dropna(how='all',subset=[u'Country', u'Man syst', u'Sp group'])
    two=two.dropna(how='all',subset=[u'Country', u'Man syst', u'Sp group'])
    three=three.dropna(how='all',subset=[u'Country', u'Man syst', u'Sp group'])
    four=four.dropna(how='all',subset=[u'Country', u'Man syst', u'Sp group'])

    #remove duplicates rows
    one.drop_duplicates(inplace=True,keep='last')
    two.drop_duplicates(inplace=True,keep='last')
    three.drop_duplicates(inplace=True,keep='last')
    four.drop_duplicates(inplace=True,keep='last')

    #since in three does not take out a duplicate for UK I do it manually
    three.drop(three.index[[99]], inplace=True)


    #IF SOMETHING CHANGE IN THE SOURCE FILE THIS BELOW NEEDS TO BE UPDATED

    #remove ID 17, latvia, clearcut, fast grow deciduous, alnus glutinosa that is a duplicate i.e. index 133
    #remove ID 17, Lituania, clearcut, fast grow deciduous, alnus glutinosa that is a duplicate i.e. index 148
    one.drop([133,148], inplace=True)
    two.drop([133,148], inplace=True)
    three.drop([133,148], inplace=True)
    four.drop([133,148], inplace=True)

    #cobine all together
    alltog=one.merge(two,how='outer',on=[u'Country', u'Man syst', u'Sp group'])
    alltog=alltog.merge(three,how='outer',on=[u'Country', u'Man syst', u'Sp group'])
    alltog=alltog.merge(four,how='outer',on=[u'Country', u'Man syst', u'Sp group'])

    #remove tabs
    alltog['Man syst']=alltog['Man syst'].str.lstrip('\t')

    #add ecoregions
    eco=pd.read_csv(eco)
    alltog=alltog.merge(eco,how='left',left_on='Country',right_on='Country_quest')



    #rename change withespace with underscore in column names
    alltog.rename(columns=lambda x: x.replace(' ','_'),inplace=True)

    #add management and species codes
    man_code=pd.read_excel(man_c,sheetname='man_code')
    alltog=alltog.merge(man_code,how='left',on=[u'Man_syst'])
    sp_code=pd.read_excel(sp_c,sheetname='sp_code')
    alltog=alltog.merge(sp_code,how='left',on=[u'Sp_group'])
    
    #combine man and sp
    alltog['man_sp']=alltog['Man_syst_code'].astype(str) + '-' + alltog['Sp_gr_code'].astype(str)
    # sp_man.drop(["Man_syst_code",'Sp_gr_code'],inplace=True, axis=1)

    #change name to make the graphs better
    alltog.rename(columns={'Ecore_WP5': 'Ecoregion', 'man_sp': 'FU'}, inplace=True)

    #correct all the shit has been done
    #rotations
    alltog.Rotation.replace({'5':'1-5','12':'11-15','20':'16-20','30':'26-30','50-70':'56-60','60':'56-60','70':'66-70','70-80':'76-80',
                '80':'76-80','80-100':'86-90','80-120':'101-105','90':'86-90','100':'96-100','100-120':'111-115','105':'101-105',
                '120':'116-120','140':'136-140','150':'146-150','160':'156-160','160-180':'171-175','200':'196-200'},inplace=True)
    #density
    alltog.Den_fresh.replace({820.0:0.820,760.0:0.760,800.0:0.8,1025.0:1.025},inplace=True)
    alltog.Den_dried.replace({430.0:0.430,490.0:0.490},inplace=True)
    alltog['OMS-Den_fre'].replace({950:0.950},inplace=True)
    return alltog

def add_pedigre(df,ped_path):
    """function that add the values of pedigree matrix """
#     cols=['Country', 'Man_syst', 'Sp_group', 'Reliability', 'Completeness','Temporal correlation',
#           'Geographical correlation','Further technological correlation', 'DQD', 'Quality assessment']
    cols=['Country', 'Man_syst', 'Sp_group', 'Rel', 'Compl', 'T_cor', 'G_cor','FT_cor', 'DQD', 'QA']
    ped=pd.read_excel(ped_path)[cols]
    mer=df.merge(ped,how='inner',on=['Country', 'Man_syst', 'Sp_group'])
    return mer[cols+[x for x in mer.columns if x not in cols]]
    
def filter_pedigre_unmanaged(df,ped_path,qual_val):
    """function that filter the cols based on the data quality of pedigree matrix passed as list, takes out also unmanaged
    add the values  """
    cols=['Country', 'Man_syst', 'Sp_group', 'Rel', 'Compl', 'T_cor', 'G_cor','FT_cor', 'DQD', 'QA']
    #~ if all(x in df.columns for x in cols):
        #~ df=df[df['QA'].isin(qual_val)]
        #~ df[cols+[x for x in df.columns if x not in cols]]
    #~ else:
        #~ ped=pd.read_excel(ped_path)[cols]
        #~ df=df.merge(ped,how='right',on=['Country', 'Man_syst', 'Sp_group'])
        #~ df=df[df['QA'].isin(qual_val)]
        #~ df[cols+[x for x in df.columns if x not in cols]]
    if not all(x in df.columns for x in cols):
        ped=pd.read_excel(ped_path)[cols]
        df=df.merge(ped,how='inner',on=['Country', 'Man_syst', 'Sp_group'])
    df=df[(df['QA'].isin(qual_val)) & (df['Man_syst']!='Unmanaged forests')]
    df[cols+[x for x in df.columns if x not in cols]]
    return df

    

def clean_sankeymatic(alltog,man_col,sp_col):
    """function that takes alltog and print out the data in the format of sankeymatic for ecoregion,
     species groups and management"""

    # counts ecoregion/sp groups
    eco_sp=alltog[['Ecoregion', sp_col]]
    eco_sp_c=eco_sp.groupby(['Ecoregion',sp_col]).agg(len)
    eco_sp_c = pd.DataFrame(eco_sp_c, columns=['count'])
    eco_sp_c.reset_index(inplace=True)
    eco_sp_c['sankeymatic']=eco_sp_c['Ecoregion'] + ' [' + eco_sp_c['count'].astype(str) + '] ' + eco_sp_c[sp_col]

    # counts ecoregion/management
    sp_man=alltog[[sp_col,  man_col]]
    sp_man_c=sp_man.groupby([sp_col, man_col]).agg(len)
    sp_man_c = pd.DataFrame(sp_man_c, columns=['count'])
    sp_man_c.reset_index(inplace=True)
    sp_man_c['sankeymatic']=sp_man_c[sp_col].astype(str) + ' [' + sp_man_c['count'].astype(str) + '] ' + sp_man_c[man_col].astype(str)

    #output to copy paste in sankeymatic
    sp_outp=eco_sp_c.sankeymatic.astype(str).values
    for exc_sp in sp_outp:
        print (exc_sp)
        
    print()
    #output to copy paste in sankeymatic
    man_outp=sp_man_c.sankeymatic.astype(str).values
    for exc_man in man_outp:
        print (exc_man)

        
##################################INTERVENTIONS############################################

def initial_clean_interv(file_one,file_two,file_mach):
    """remove a series of cleaning steps to the two matrixes"""
    # #remove empty rows
    
    one=pd.read_excel(file_one)
    two=pd.read_excel(file_two)
    machine=pd.read_excel(file_mach)
    
    
    #dropna
    one=one.dropna(how='all',subset=[u'Country', u'Management system', u'Species group','interv num'])
    two=two.dropna(how='all',subset=[u'Country', u'Management system', u'Species group','interv num'])

    #remove duplicates rows
    one.drop_duplicates(inplace=True,keep='last')
    two.drop_duplicates(inplace=True,keep='last')

    #rename change withespace with underscore in column names
    one.rename(columns=lambda x: x.replace(' ','_'),inplace=True)
    two.rename(columns=lambda x: x.replace(' ','_'),inplace=True)
    one.rename(columns=lambda x: x.replace('-','_'),inplace=True)
    two.rename(columns=lambda x: x.replace('-','_'),inplace=True)

    # strip intervention from u'interv_num and change to int
    one.interv_num=one.interv_num.str.strip('intervention')
    two.interv_num=two.interv_num.str.strip('intervention')

    #replace - with nan in timing of internvetion in one (two does not have this field)
    # one.Timing_of_intervention.replace({'-',''},inplace=True)
    one['Timing_of_intervention']=one['Timing_of_intervention'].str.lstrip('-')

    #change to integer interv_num and timing_of_interv
    one['interv_num']=pd.to_numeric(one['interv_num']) 
    two['interv_num']=pd.to_numeric(two['interv_num'])
    one['Timing_of_intervention']=pd.to_numeric(one['Timing_of_intervention']) 

    ## remove tabs
    one['Management_system']=one['Management_system'].str.lstrip('\t')
    two['Management_system']=two['Management_system'].str.lstrip('\t')
    
    
    #change name clearcut to make the same of FINALISSIMO
#     one.Management_system.replace({'Even-aged forest: Uniform clear-cut system':'Even-aged forest-Uniform clear-cut system'},inplace=True)
#     two.Management_system.replace({'Even-aged forest: Uniform clear-cut system':'Even-aged forest-Uniform clear-cut system'},inplace=True)
    
    return one,two


# In[39]:

def clean_dup_rows_int(one_or_two):
    """clean duplicated rows deleting when necessary and recount the intervention number when there are duplicates of them
    
    return the dataframe cleaned and sorted"""
    #first we sort (see below why)
    sort=one_or_two.sort_values([u'Country', u'Management_system', u'Species_group','interv_num'])
    sort.reset_index(drop=True,inplace=True)

    #then we get the duplicates indexes (pandas give only the one duplicate so we sort first and after we take index of duplicates and of the previous one)
    duplic_one= [i for i,x in enumerate(sort.duplicated(subset=[u'Country', u'Management_system', u'Species_group','interv_num']).values) if x == True]
    duplic_one= list(set(duplic_one+[x-1 for x in duplic_one]))
    duplic_one.sort()

    #cleaning of duplicates
    sort.loc[25,'interv_num']=12 #austria

    for i,x in enumerate([458, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470]): 
         sort.loc[x,'interv_num']=i+1

    for i,x in enumerate(list(range(471,484))): #Fin,clear-cut, sh tol con
        sort.loc[x,'interv_num']=i+1

    for i,x in enumerate(list(range(1167,1179))): #pol,shelt, Lig dem con
        sort.loc[x,'interv_num']=i+1

    for i,x in enumerate(list(range(1179,1191))): #pol,shelt, sh tol con
        sort.loc[x,'interv_num']=i+1

    for i,x in enumerate(list(range(1191,1205))): #pol
        sort.loc[x,'interv_num']=i+1

    for i,x in enumerate(list(range(1218,1227))): #pol
        sort.loc[x,'interv_num']=i+1  

    for i,x in enumerate(list(range(1227,1239))): #pol
        sort.loc[x,'interv_num']=i+1   

    for i,x in enumerate(list(range(1239,1249))): #pol
        sort.loc[x,'interv_num']=i+1   

    
    sort.drop(sort.index[[459]],inplace=True)#Fin,clear-cut, Lig dem con
    sort.drop(sort.index[[1181]],inplace=True) #pol,shelt, sh tol con
    sort.drop(sort.index[[1628]],inplace=True) #swit,coppice, Lig dem dec
    
    sort.reset_index(drop=True,inplace=True)
    
    return sort


# In[41]:

##########################
#TO CHECK NOT WORKING YET#
##########################
#~ def _check_duplicated_fixed(df_before,df_after):
    #~ """functiont to check how the duplicated fixed have been changed"""
    #~ 
    #~ #filter row duplicated before (do not take both both only the one that already exists)
    #~ dup=df_before.ix[df_before[[u'Country', u'Management_system', u'Species_group','interv_num']].duplicated()[
        #~ df_before[[u'Country', u'Management_system', u'Species_group','interv_num']].duplicated()==True].index.values.tolist() ]
    #~ #take only first 4 rows
    #~ dup=dup[[u'Country', u'Management_system', u'Species_group','interv_num']]
    #~ #take duplucated
#~ #     dup=df_before.merge(dup, how='right', on=['Country', 'Management_system', 'Species_group','interv_num'])
    #~ dup=df_before.reset_index().merge(dup, how="right",on=['Country', 'Management_system', 'Species_group','interv_num']).set_index('index') # to keep the indez
#~ 
#~ 
    #~ #filter row duplicated after (do not take both both only the one that already exists)
    #~ no_dup=df_after.ix[dup.index.values.tolist()]
    #~ no_dup['MERGED']='YES'
    #~ 
#~ #     no_dup=df_after.ix[df_before[[u'Country', u'Management_system', u'Species_group','interv_num']].duplicated()[df_before[[u'Country', u'Management_system', u'Species_group','interv_num']].duplicated()==True].index.values.tolist() ]
    #~ #take only first 4 rows
#~ #     no_dup=no_dup[[u'Country', u'Management_system', u'Species_group','interv_num']]
#~ #     #take duplucated
#~ #     no_dup=df_after.merge(no_dup, how='right', on=['Country', 'Management_system', 'Species_group','interv_num'])
#~ 
    #~ #concatenate the two
    #~ both=pd.concat([dup,no_dup],ignore_index=True)
    #~ both=both[no_dup.columns].sort_values(['Country', 'Management_system', 'Species_group','interv_num'])
    #~ return no_dup
#~ # _check_duplicated_fixed(one_in,one_no_dup)
#~ #.to_excel('/home/giuseppec/Downloads/duplic.xls')


# In[46]:

def machineries_interventions(alltog,mach_file):
    """function that work on the machineries importing and converting the spreadsheet id-machine correspondence and does some cleaning-conversion of it
    and of the interventions"""
    
    machine=pd.read_excel(mach_file)
        
    #rename machineries
    machine_first=machine.rename(columns={'ID': 'Type_of_Main_equipment','equipment':"Main_equip"})
    machine_add=machine.rename(columns={'ID': 'Type_of_Additional_equipment','equipment':"Add_equip"})
    
    #add machieneries names
    alltog=alltog.merge(machine_first,how='left',on='Type_of_Main_equipment')
    alltog=alltog.merge(machine_add,how='left',on='Type_of_Additional_equipment')

    # replace other in interventions and equipments
    alltog.ix[alltog.Type_of_intervention == 'other', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.Main_equip.isnull(), 'Main_equip'] = alltog.if_other_specify_M_equip
    alltog.ix[alltog.Add_equip.isnull(), 'Add_equip'] = alltog.if_other_specify_A_equip  
    
    # change all the brashing saw to make them consisten
    alltog.ix[alltog.Main_equip == 'clearing saw' , 'Main_equip'] = 'brushing saw'
    alltog.ix[alltog.Main_equip =='brush cutter+manual', 'Main_equip'] = 'brushing saw'
    alltog.ix[alltog.Main_equip =='brush cutter', 'Main_equip'] = 'brushing saw'
    alltog.ix[alltog.Main_equip =='Brush cutter', 'Main_equip'] = 'brushing saw'
    alltog.ix[alltog.Main_equip =='brush cutter + chainsaw', 'Main_equip'] = 'brushing saw'

    #when necessary (i.e. clearer explanation) replacement of  Type_of_intervention with if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'bark / cork harvesting', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'pruning', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'ripping&disking', 'Type_of_intervention'] = 'ripping & disking'
    alltog.ix[alltog.if_other_specify_interv == 'cleaning forest area from branches', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'early cleaning', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'early cleaning (respacing)', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'early tending', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'late cleaning', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'late cleaning (respacing)', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'late tending', 'Type_of_intervention'] = alltog.if_other_specify_interv
    alltog.ix[alltog.if_other_specify_interv == 'mechanical processing of logging waste (chips - biomass for bioenergy)', 'Type_of_intervention'] = alltog.if_other_specify_interv

    #Drops useless columns
    alltog.drop(['Rule_for_the_timing_intervention','if_other_specify_timing_int',
                             'Rule_for_the_intensity_of_intervention','if_other_specify_rule_inter'], axis=1, inplace=True)
                             
    return alltog.sort_values(['Country', 'Management_system', 'Species_group','interv_num'])



# In[50]:

def clean_finalissimo(final):
    """import and clean finalissimo"""
    #import file finalissimo
    finalis=pd.read_excel(final)
    #add underscore
    finalis.rename(columns=lambda x: x.replace(' ','_'),inplace=True)
    
    #replace - with nan,leave only number in intervention and change to numeric
    finalis['Timing_of_intervention']=finalis['Timing_of_intervention'].str.lstrip('-')
    finalis.interv_num=finalis.interv_num.str.strip('intervention')
    finalis['interv_num']=pd.to_numeric(finalis['interv_num']) 
    #cahge clearcut name
    finalis.Management_system.replace({'Even-aged forest-Uniform clear-cut system':'Even-aged forest: Uniform clear-cut system'},inplace=True)

    #for now deleted cable skidder or woodliner cause duplicate in most cases (not all)
    finalis.ix[finalis.second_additional_equipment == '+firewood processor' , 'second_additional_equipment'] = 'firewood processor'
    finalis.ix[finalis.second_additional_equipment == 'cable skidder or woodliner' , 'second_additional_equipment'] = np.nan
    
    #delete some wrong things
    finalis=finalis[~((finalis.ID == 1) & (finalis['Respondent_ID']==21))] # ('Estonia', 'Even-aged forest with shelterwood', 'Light demanding conifers', '115', 'regeneration felling')

    return finalis


# In[43]:

def combine_all_final(alltog,finalis,ecoregion,management_codes,species_codes):
    """merge (taking the proper columns) and reorder columns of alltog and finalissimo
    I bascially just took finalissimo and added the extra column present in alltog
    """
    
# # FOR THIS FINALISSIMO IS ADDED TO ALLTOG (one I am NOT using now but need to check which of the two is correct)
    #take cols needed from alltog
    #~ all_code=alltog[['ID', 'Respondent_ID', 'Country', 'Management_system', 'Species_group', 'interv_num', 'Type_of_intervention', 'if_other_specify_interv',
     #~ 'Timing_of_intervention', 'Specie(s)_concerned_by_intervention', 'Pre_int_stock', 'Pre_int_BA', 'Intensity_of_intervention', 'Main_equip', 
     #~ 'Power_(CV)_M', 'Mass_(t)_M_n', 'Hours_of_use_during_whole_life_M', 'Consumption_(l/h)', 'h/ha', 'm3/h', 'fresh_t/h', 'Add_equip', 'Mass_(t)_A', 
     #~ 'Hours_of_use_during_whole_life_A', 'input_1', 'active_pr1', 'Amount_1', 'input_2', 'active_pr2', 'Amount_2', 'Stemwood', 'Stem_and_residues', 'Stumps']]
    #~ all_code.rename(columns={'Type_of_intervention':'type_of_intervention'},inplace=True) # in finalissimo is lower case
#~ 
    #~ #take cols needed from finaliss
    #~ fin_code=finalis[['ID', 'Respondent_ID', 'Country', 'Management_system', 'Species_group', 'h/ha_2', 'm3/h_2', 'fresh_t/h_2', 'm3_over_bark_Logs',
                      #~ 'm3_under_bark_Logs', 'dry_t_Logs', 'm3_over_bark_pulp', 'm3_under_bark_pulp', 'dry_t_pulp', 'm3_over_bark_Firewood', 
                      #~ 'm3_under_bark_Firewood', 'Stacked_cubic_meter_Firewood', 'dry_t_Firewood', 'm3_chips', 'Loose_cubic_meter_chips', 
                      #~ 'dry_t_chips', 'Loose_cubic_meter_stumps/ha', 'dry_t_chips_stumps', 'intervention', 'second_additional_equipment']]
    #~ #add finalissimo to altog  
    #~ both=all_code.merge(fin_code,how='outer',on=['ID','Respondent_ID','Country', 'Management_system', 'Species_group'],indicator=True)


#~ # FOR THIS  ALLTOG IS ADDED TO FINALISSIMO (one I am using now but need to check which of the two is correct)

    #~ #filter only needed columns from altog (one I am using now but need to check which of the two is correct)
    all_code=alltog[['ID', 'Respondent_ID', 'Country', 'Management_system', 'Species_group','Specie(s)_concerned_by_intervention', 
                     'Pre_int_stock', 'Pre_int_BA', 'Intensity_of_intervention', 'input_1', 'active_pr1', 'Amount_1',
                     'input_2', 'active_pr2', 'Amount_2', 'Stemwood', 'Stem_and_residues', 'Stumps']]
            
    # add altog to finalissimo (one I am using now but need to check which of the two is correct)
    both=finalis.merge(all_code,how='outer',on=['ID','Respondent_ID','Country', 'Management_system', 'Species_group'],indicator=True)
    
    #deal with old stuff not in finalissimo
    old=both[both._merge=='right_only'][['ID','Respondent_ID','Country', 'Management_system', 'Species_group']]
    old=old.merge(alltog,how='left',on=['ID','Respondent_ID','Country', 'Management_system', 'Species_group'])
    #fix missing things in old    
    old.rename(columns={'Type_of_intervention':'type_of_intervention',  'Type_of_Main_equipment':'type_of_main_equipment'},inplace=True)
    old['Expr1035', 'fresh_t/h_2', 'h/ha_2', 'intervention', 'm3/h_2', 'second_additional_equipment']=np.nan
    #take only internvetion we need
    old=old[old.type_of_intervention.isin(['building game protection fence','planting','pruning','tending'])]
    
    #deal with ones only in finalissimo
    both=both[both._merge=='both'].drop('_merge', axis=1)

    cols=both.columns

    #concat old and new
    both=pd.concat([both,old])[cols]

#~ ##############


    #add ecoregions
    eco=pd.read_csv(ecoregion)
    both=both.merge(eco,how='left',left_on='Country',right_on='Country_quest')
    
    #add management and species codes
    man_code=pd.read_excel(management_codes,sheetname='man_code')
    both=both.merge(man_code,how='left',
                    left_on=[u'Management_system'],
                    right_on=['Man_syst'])
    sp_code=pd.read_excel(species_codes,sheetname='sp_code')
    both=both.merge(sp_code,how='left',
                    left_on=[u'Species_group'],
                    right_on=['Sp_group'])
    

    

#     both=both[['ID', 'Respondent_ID', 'Ecore_WP5', u'Ecore_name','Country',"Man_syst_code",'Management_system','Sp_gr_code','Species_group', 'interv_num', 'Type_of_intervention', 'if_other_specify_interv',
#      'Timing_of_intervention', 'Specie(s)_concerned_by_intervention', 'Pre_int_stock', 'Pre_int_BA', 'Intensity_of_intervention', 'Main_equip',
#      'Power_(CV)_M', 'Mass_(t)_M_n', 'Hours_of_use_during_whole_life_M', 'Consumption_(l/h)', 'h/ha', 'm3/h', 'fresh_t/h', 'Add_equip', 'Mass_(t)_A',
#      'Hours_of_use_during_whole_life_A', 'h/ha_2', 'm3/h_2', 'fresh_t/h_2', 'input_1', 'active_pr1', 'Amount_1', 'input_2', 'active_pr2', 'Amount_2',
#      'Stemwood', 'Stem_and_residues', 'Stumps', 'm3_over_bark_Logs', 'm3_under_bark_Logs', 'dry_t_Logs', 'm3_over_bark_pulp', 'm3_under_bark_pulp',
#      'dry_t_pulp', 'm3_over_bark_Firewood', 'm3_under_bark_Firewood', 'Stacked_cubic_meter_Firewood', 'dry_t_Firewood', 'm3_chips', 'Loose_cubic_meter_chips',
#      'dry_t_chips', 'Loose_cubic_meter_stumps/ha', 'dry_t_chips_stumps', 'second_additional_equipment', 'intervention']]

    #rename Main_equip to not change the graphs in R
    both.rename(columns={'type_of_main_equipment':'Main_equip'},inplace=True)
    both.rename(columns={'Type_of_Additional_equipment':'Add_equip'},inplace=True)
    if 'Expr1035' in both.columns:
        both.drop('Expr1035',axis=1,inplace=True)
    
    both['FU']=both['Man_syst_code'].astype(str) + '-' + both['Sp_gr_code'].astype(str)
#     both.drop(["Man_syst_code",'Sp_gr_code'],inplace=True, axis=1)

    #rename fina to regeneration felling
    both.intervention.replace({'final felling':'regeneration felling'},inplace=True)


    return both.sort_values(['Country', 'Management_system', 'Species_group','interv_num'])
    
    
def _helper_dup(ind_1,ind_2,ind_3,ind_4,group,name): 
    """helper function for recombine_dup_rows_into_one """
    new_row=group.iloc[ind_1:ind_2,]
#          check if add_equip are empty or not in first and second row 
    if (pd.notnull(new_row.iloc[0]['Add_equip'])): 
        print('Add_equip in first row is not empty, check:\n',name,'\n')
    if (pd.notnull(group.iloc[ind_3:ind_4,].iloc[0]['Add_equip'])): #check if value of add equip is nan in second row
        print('Add_equip in second row is not empty, check:\n',name,'\n')
    #add main equip of second row to the first after checking fi add machine is nan
    new_row['Add_equip']=group.iloc[ind_3:ind_4,].iloc[0]['Main_equip'] #this take the value of main eq in the second row

    #check if h/ha_2 are empty or not in first and second row 
    if (pd.notnull(new_row.iloc[0]['h/ha_2'])): 
        print('h/ha_2 in first row is not empty, check:\n',name,'\n')
    if (pd.notnull(group.iloc[ind_3:ind_4,].iloc[0]['h/ha_2'])): #check if value of add equip is nan in second row
        print('h/ha_2 in second row is not empty, check:\n',name,'\n')             
    #add h/ha of second row to the first after checking if h/ha_2 is nan
    new_row['h/ha_2']=group.iloc[ind_3:ind_4,].iloc[0]['h/ha'] #this take the value of main eq in the second row

    # check if m3/h_2 are empty or not in first and second row 
    if (pd.notnull(new_row.iloc[0]['m3/h_2'])): 
        print('m3/h_2 in first row is not empty, check:\n',name,'\n')
    if (pd.notnull(group.iloc[ind_3:ind_4,].iloc[0]['m3/h_2'])): #check if value of add equip is nan in second row
        print('m3/h_2 in second row is not empty, check:\n',name,'\n')                    
    #add m3/h of second row to the first after checking if m3/h_2 is nan
    new_row['m3/h_2']=group.iloc[ind_3:ind_4,].iloc[0]['m3/h'] #this take the value of main eq in the second row

    # check if fresh_t/h_2 are empty or not in first and second row 
    if (pd.notnull(new_row.iloc[0]['fresh_t/h_2'])): 
        print('fresh_t/h_2 in first row is not empty, check:\n',name,'\n')
    if (pd.notnull(group.iloc[ind_3:ind_4,].iloc[0]['fresh_t/h_2'])): #check if value of add equip is nan in second row
        print('fresh_t/h_2 in second row is not empty, check:\n',name,'\n')            
    #add fresh_t/h of second row to the first after checking if fresh_t/h_2 is nan
    new_row['fresh_t/h_2']=group.iloc[ind_3:ind_4,].iloc[0]['fresh_t/h'] #this take the value of main eq in the second row

#############################TEST###########################
# NEED TO SEE WHAT TO DO WITH  
    #add main equip of second row to the first after checking fi add machine is nan
    new_row['Power_(CV)_M_2']=group.iloc[ind_3:ind_4,].iloc[0]['Power_(CV)_M'] #this take the value of main eq in the second row

    #add Mass_(t)_M_n of second row to the first after checking if Mass_(t)_M_n_2 is nan
    new_row['Mass_(t)_A']=group.iloc[ind_3:ind_4,].iloc[0]['Mass_(t)_M_n'] #this take the value of main eq in the second row

    #add Hours_of_use_during_whole_life_M of second row to the first after checking if Hours_of_use_during_whole_life_M_2 is nan
    new_row['Hours_of_use_during_whole_life_A']=group.iloc[ind_3:ind_4,].iloc[0]['Hours_of_use_during_whole_life_M'] #this take the value of main eq in the second row

    #add Consumption_(l/h) of second row to the first after checking if Consumption_(l/h)_2 is nan
    new_row['Consumption_(l/h)_2']=group.iloc[ind_3:ind_4,].iloc[0]['Consumption_(l/h)'] #this take the value of main eq in the second row
#############################TEST###########################

    return new_row

def recombine_dup_rows_into_one(combined_df):
    """this function when the same interventions has  been reported in two cols (for instance like in slovakia 
    annd other countries where harvesting and hauling have been reported in two separate cols) combine both
    into one putting the main_machine of the second in the add_machine of the first row and doing the same
    for the productivities (e.g. m3/h of the second gets moved to m3/h_2 of the first)
    
    -takes the result of combine_all_final as argument
    
    """
    

    keys=['Country', 'Management_system', 'Species_group','Timing_of_intervention', 'type_of_intervention',]
#     'm3_over_bark_Logs','m3_under_bark_Logs',
#                 'dry_t_Logs','m3_over_bark_pulp', 'm3_under_bark_pulp', 'dry_t_pulp', 'm3_over_bark_Firewood','m3_under_bark_Firewood','Stacked_cubic_meter_Firewood',
#                 'dry_t_Firewood','m3_chips','Loose_cubic_meter_chips','dry_t_chips','Loose_cubic_meter_stumps/ha','dry_t_chips_stumps']

    
    #fill nan to avoid prob in grouping
    comb_empt=combined_df.copy(deep=True)
    comb_empt[keys]=combined_df[keys].fillna('empty')

    #create new empty df with columns of combined
#     combined_reduced=pd.DataFrame(columns=comb_empt.columns) # old one without adding also the cols with 'Power_(CV)_M', 'Mass_(t)_M_n','Hours_of_use_during_whole_life_M', 'Consumption_(l/h)'
    combined_reduced=pd.DataFrame(columns=(list(comb_empt.columns)+ ['third_equip','Power_(CV)_M_2', 'Consumption_(l/h)_2',
                                                                    'Power_(CV)_M_3', 'Mass_(t)_M_n_3','Hours_of_use_during_whole_life_M_3', 'Consumption_(l/h)_3',
                                                                    'h/ha_3', 'm3/h_3', 'fresh_t/h_3'])) #test to add machineries carachteristics
    cols=combined_reduced.columns
    #groupby
    grouped = comb_empt.groupby(keys)
    dup=pd.DataFrame(columns=comb_empt.columns)
    
    #check if there are more than 2 duplicates
    print('THE ERROR REPORTED FOR FRANCE BELOW HAVE TO BE NEGLECTED, ALREADY CHECKED')
    
    for name, group in grouped:
        #just add the row when unique or when there are 
        if len(group)==1:
            combined_reduced=pd.concat([combined_reduced,group])
        # for the ones that have two machineries for each intervention
        elif len(group)==2:
            # to check legnth
            dup=pd.concat([dup,group]) 
        
            for x in [[0,1,1,2]]:
                #append the first row modified to the new df
                combined_reduced=pd.concat([combined_reduced,_helper_dup(x[0],x[1],x[2],x[3],group,name)])
        else:
            dup=pd.concat([dup,group]) 
            if name in [('CzechRepublic', 'Even-aged forest with shelterwood', 'Shade tolerant conifers', '100', 'regeneration felling'),
                         ('CzechRepublic', 'Even-aged forest: Uniform clear-cut system', 'Shade tolerant conifers', '100', 'clear cutting')]:
                for x in [[0,1,3,4],[1,2,2,3]]:
                    combined_reduced=pd.concat([combined_reduced,_helper_dup(x[0],x[1],x[2],x[3],group,name)])


            else:
                new_row=group.iloc[0:1,]

                #add main equip of second row to the first after checking fi add machine is nan
                new_row['Add_equip']=group.iloc[1:2,].iloc[0]['Main_equip'] #this take the value of main eq in the second row

                #add h/ha of second row to the first after checking if h/ha_2 is nan
                new_row['h/ha_2']=group.iloc[1:2,].iloc[0]['h/ha'] #this take the value of main eq in the second row

                #add m3/h of second row to the first after checking if m3/h_2 is nan
                new_row['m3/h_2']=group.iloc[1:2,].iloc[0]['m3/h'] #this take the value of main eq in the second row

                #add fresh_t/h of second row to the first after checking if fresh_t/h_2 is nan
                new_row['fresh_t/h_2']=group.iloc[1:2,].iloc[0]['fresh_t/h'] #this take the value of main eq in the second row

                #add main equip of second row to the first after checking fi add machine is nan
                new_row['Power_(CV)_M_2']=group.iloc[1:2,].iloc[0]['Power_(CV)_M'] #this take the value of main eq in the second row

                #add Mass_(t)_M_n of second row to the first after checking if Mass_(t)_M_n_2 is nan
                new_row['Mass_(t)_A']=group.iloc[1:2,].iloc[0]['Mass_(t)_M_n'] #this take the value of main eq in the second row

                #add Hours_of_use_during_whole_life_M of second row to the first after checking if Hours_of_use_during_whole_life_M_2 is nan
                new_row['Hours_of_use_during_whole_life_A']=group.iloc[1:2,].iloc[0]['Hours_of_use_during_whole_life_M'] #this take the value of main eq in the second row

                #add Consumption_(l/h) of second row to the first after checking if Consumption_(l/h)_2 is nan
                new_row['Consumption_(l/h)_2']=group.iloc[1:2,].iloc[0]['Consumption_(l/h)'] #this take the value of main eq in the second row


                #######third######

                #add main equip of second row to the first after checking fi add machine is nan
                new_row['third_equip']=group.iloc[1:2,].iloc[0]['Main_equip'] #this take the value of main eq in the second row

                #add h/ha of second row to the first after checking if h/ha_2 is nan
                new_row['h/ha_3']=group.iloc[1:2,].iloc[0]['h/ha'] #this take the value of main eq in the second row

                #add m3/h of second row to the first after checking if m3/h_2 is nan
                new_row['m3/h_3']=group.iloc[1:2,].iloc[0]['m3/h'] #this take the value of main eq in the second row

                #add fresh_t/h of second row to the first after checking if fresh_t/h_2 is nan
                new_row['fresh_t/h_3']=group.iloc[1:2,].iloc[0]['fresh_t/h'] #this take the value of main eq in the second row

                #add main equip of second row to the first after checking fi add machine is nan
                new_row['Power_(CV)_M_3']=group.iloc[1:2,].iloc[0]['Power_(CV)_M'] #this take the value of main eq in the second row

                #add Mass_(t)_M_n of second row to the first after checking if Mass_(t)_M_n_2 is nan
                new_row['Mass_(t)_M_n_3']=group.iloc[1:2,].iloc[0]['Mass_(t)_M_n'] #this take the value of main eq in the second row

                #add Hours_of_use_during_whole_life_M of second row to the first after checking if Hours_of_use_during_whole_life_M_2 is nan
                new_row['Hours_of_use_during_whole_life_M_3']=group.iloc[1:2,].iloc[0]['Hours_of_use_during_whole_life_M'] #this take the value of main eq in the second row

                #add Consumption_(l/h) of second row to the first after checking if Consumption_(l/h)_2 is nan
                new_row['Consumption_(l/h)_3']=group.iloc[1:2,].iloc[0]['Consumption_(l/h)'] #this take the value of main eq in the second row

                combined_reduced=pd.concat([combined_reduced,new_row])
                # to check legnth
#                 dup=pd.concat([dup,group])            
                print('there are more than 2 dupicates per row, chek:')
                print(name)

    combined_reduced.replace('empty',np.nan,inplace=True)    

    return combined_reduced[cols].sort_values(['Country', 'Management_system', 'Species_group','interv_num']),dup


def export_efi_interventions(df,filepath):
    """function that export the df for hans verkek"""    
    df[['Country', 'Management_system', 'Species_group','interv_num', 'Timing_of_intervention', 'type_of_intervention',
       
    'Main_equip','Power_(CV)_M', 'Mass_(t)_M_n','Consumption_(l/h)', 'Hours_of_use_during_whole_life_M','h/ha', 'm3/h','fresh_t/h',

    'Add_equip','Power_(CV)_M_2','Mass_(t)_A', 'Consumption_(l/h)_2','Hours_of_use_during_whole_life_A','h/ha_2','m3/h_2', 'fresh_t/h_2',

    'third_equip','Power_(CV)_M_3','Mass_(t)_M_n_3','Hours_of_use_during_whole_life_M_3','Consumption_(l/h)_3','h/ha_3','m3/h_3',
     'fresh_t/h_3','second_additional_equipment',
    
    'Stemwood', 'Stem_and_residues', 'Stumps', 'm3_over_bark_Logs', 'm3_under_bark_Logs', 'dry_t_Logs','m3_over_bark_pulp', 'm3_under_bark_pulp',
    'dry_t_pulp','m3_over_bark_Firewood', 'm3_under_bark_Firewood', 'Stacked_cubic_meter_Firewood', 'dry_t_Firewood', 'm3_chips',
    'Loose_cubic_meter_chips', 'dry_t_chips', 'Loose_cubic_meter_stumps/ha', 'dry_t_chips_stumps', 'Specie(s)_concerned_by_intervention',
    'Pre_int_stock', 'Pre_int_BA', 'Intensity_of_intervention', 'input_1', 'active_pr1', 'Amount_1', 'input_2', 'active_pr2', 'Amount_2',
    
#     'Country_quest', 'Ecore_WP5','Ecore_name', 'country_EFI_GTM', 'country_Code', 'Country_WP5','proxy_country_wp2', 'Country_UNECE', 'Country_WP2',
#     'Man_syst','Man_syst_code', 'Man_syst_abbreviation', 'Sp_group', 'Sp_gr_code','Sp_gr_abbreviation', 'FU', 
    ]].to_excel(filepath,index=False)
    
def export_file(df,filepath,list_cols_df,list_new_names_cols=None):
    """function that export the df for hans verkek"""    
    to_exp=df[list_cols_df]
    if list_new_names_cols is not None:
        to_exp.columns=list_new_names_cols
    return to_exp.to_excel(filepath,index=False)

##############
#GENERAL FILE#
##############

# Gen_one=pd.read_excel('PAPER_1_Gen_1_rule_thin_1.xls')
# Gen_two=pd.read_excel('PAPER_1_Gen_2_rules.xls')
# Gen_three=pd.read_excel('PAPER_1_Gen_3_genetic_res.xls')
# Gen_four=pd.read_excel('PAPER_1_Gen_4_eco_serv.xls')

# ecoregion='/media/giuseppec/25F62A4E5FEED162/work/FORMIT/WP3/LCA/correspondence_file/countr_ecor_correspondence.csv'
# management_codes='/media/giuseppec/25F62A4E5FEED162/work/FORMIT/WP3/LCA/correspondence_file/Sp_man_codes.xls'
# species_codes='/media/giuseppec/25F62A4E5FEED162/work/FORMIT/WP3/LCA/correspondence_file/Sp_man_codes.xls'

# gen_all=import_general_file(Gen_one,Gen_two,Gen_three,Gen_four,ecoregion,management_codes,species_codes)
# # gen_all.to_excel('general_cleaned.xls')


# In[56]:

###################
#INTERVENTION FILE#
###################

# # files
# finalissimo='/media/giuseppec/25F62A4E5FEED162/Dropbox/Dropbox/Formit (1)/Survey/Most_updated_questionnaires/160619_FINALISSIMO.xls'
# ecoregion='/media/giuseppec/25F62A4E5FEED162/work/FORMIT/WP3/LCA/correspondence_file/countr_ecor_correspondence.csv'
# mach='equipment.xls'

# #imports
# int_one='PAPER_1_int_1_hours.xls'
# int_two='PAPER_1_int_2_harv_amount.xls'


# # import and first cleaning
# one_in,two_in=initial_clean_interv(int_one,int_two,mach)
# #fix duplicates
# one_no_dup=clean_dup_rows_int(one_in)
# two_no_dup=clean_dup_rows_int(two_in)

# #merge the two files
# alltog=one_no_dup.merge(two_no_dup,how='outer',on=['ID','Respondent_ID','Country', u'Management_system', u'Species_group','interv_num'],indicator=True)

# #clean alltogether
# alltog=machineries_interventions(alltog,mach)

# # #import file finalissimo
# finalix=clean_finalissimo(finalissimo)

# # #merge finalissimo with alltog

# merged_fin_all=combine_all_final(alltog,finalix)
# # merged_fin_all.to_excel('intervention_cleaned.xls')




