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
	
	

	
