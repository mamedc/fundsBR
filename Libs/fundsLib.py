def readBlcBlock(blk, folder):

    '''
    Read unziped 'BLC' type block data from folder returning data frame.
    
    Input:
      blk, block of data to be read (integer 1 to 8)
      folder, path to unziped files
    
    Output:
      Dataframe containing the data
      
    '''
    df = pd.DataFrame()
    unzFiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    for f in unzFiles:
        s = f.split('_')

        # Type (BLC or PL)
        fType = s[2]

        # For BLC type
        if fType == 'BLC':

            # Block
            fBlk = int(s[3])

            # Year
            fYear = s[4].split('.')[0]

            if len(fYear) == 4: # Year <= 2017
                fMonth = None
                fYear = int(fYear)

            else: # Year = 2018
                fMonth = int(fYear[-2:])
                fYear = int(fYear[:4])

            if fBlk == blk: 
					
                # Read file
                print(fBlk, fYear, fMonth)
                df_ = pd.read_csv(unzipTemp + f, sep = ';', 
                     encoding = 'ISO-8859-1', 
                     low_memory = False)

                # Append
                df = df.append(df_)

    df = df.reset_index(drop = True)

    return(df)
	

def readPL(folder):

    '''
    Read unziped 'PL' type data from folder returning data frame.
    
    Input:
      folder, path to unziped files
    
    Output:
      Dataframe containing the data
      
    '''
    df = pd.DataFrame()
    unzFiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    for f in unzFiles:
        s = f.split('_')

        # Type (BLC or PL)
        fType = s[2]

        # For PL type
        if fType == 'PL':
            
            print(f)
            
            # Read file
            df_ = pd.read_csv(unzipTemp + f, sep = ';', 
                 encoding = 'ISO-8859-1', 
                 low_memory = False)

            # Append
            df = df.append(df_)

    df = df.reset_index(drop = True)

    return(df)
	
	
def interpOutlier(dfPL):
    
    '''
    Identifies the outlier value through the biggest total PL by date 
    and substitutes it with the interpolation of its neighbors values.
    
    Input: dfPL, data frame with the PLs
    Output, data frame with the corrected value
    '''
    
    dfPL_ = dfPL.copy(deep = True)
    dfSum = dfPL_.groupby(['DT_COMPTC'])['VL_PATRIM_LIQ'].sum()
    
    # Where is the outlier?
    dtOut = dfSum.sort_values(ascending = False).index[0]

    # Who is the outlier?
    aux = dfPL_[dfPL_['DT_COMPTC'] == dtOut]
    aux = aux.sort_values('VL_PATRIM_LIQ', ascending = False)
    cnpjOut = aux['CNPJ_FUNDO'].iloc[0]
    nomeOut = aux['DENOM_SOCIAL'].iloc[0]
    plOut = aux['VL_PATRIM_LIQ'].iloc[0]
    
    # Who are the neighbors and what are their PL values?
    aux = dfPL_[dfPL_['CNPJ_FUNDO'] == cnpjOut]
    aux = aux.reset_index(drop = True)
    indOut = aux[aux['DT_COMPTC'] == dtOut].index[0]

    indNeigh0 = indOut - 1
    plNeigh0 = aux.iloc[indNeigh0]['VL_PATRIM_LIQ']

    indNeigh1 = indOut + 1
    plNeigh1 = aux.iloc[indNeigh1]['VL_PATRIM_LIQ']
    
    interpolated = (plNeigh0 + plNeigh1) / 2
    
    # Update
    dfPL_.loc[(dfPL_['DT_COMPTC'] == dtOut) & \
         (dfPL_['CNPJ_FUNDO'] == cnpjOut), 'VL_PATRIM_LIQ'] = \
            interpolated
    
    # Print info
    print('{:<20s}'.format('Outlier:'))
    print('{:<20s}\n{:<20s}\n{:%Y-%m-%d}\n{:<20,.2f}'\
          .format(cnpjOut, nomeOut, dtOut, plOut))
    print('\n{:<20s} {:<20,.2f} {:<20,.2f}'.format('Neighbors values:', plNeigh0, plNeigh1))
    print('{:<20s} {:<20,.2f}'.format('Updated to:', interpolated))
        
    return(dfPL_)
	

def correctDates(x):
    
    '''
    Used in 'apply' function to dataframe columns.
    Transform dates from string to timestamp.
    If the input is 'NA', it returns also 'NA'.
    '''
    
    if x != 'NA':
        y = dt.datetime.strptime(x, "%Y-%m-%d")
    else:
        y = x
    
    return(y)
	
	
def computeBdays(row, holCalendar):
    
    '''
    Compute the business days between 'DT_COMPC' and 'DT_VENC', taking
    into account the holidays dates at 'holCalendar'
    '''
    
    if (row['DT_COMPTC'] == 'NA') | (row['DT_VENC'] == 'NA'):
        y = 'NA'
    else:
        y = np.busday_count(row['DT_COMPTC'], row['DT_VENC'], 
            holidays = list(holCalendar))
    return(y)


def computePU(row):
    
    '''
    Compute bond unitary price
    '''
    
    if row['QT_POS_FINAL'] == 0:
        y = None
    else:
        y = row['VL_MERC_POS_FINAL'] / row['QT_POS_FINAL']
    return(y)
	
	
def maxFrequency(df, column):
    
    '''
    Given a 'column' of 'df' dataframe, it returns the most frequent
    element.
    '''
    aux = list(map(list, zip(*list(Counter(df[column]).items()))))
    d0 = aux[0]
    d1 = [round(x / sum(aux[1]), 2) for x in aux[1]]
    dOut = d0[d1.index(max(d1))]
    
    return(dOut)