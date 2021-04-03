import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import calendar
import base64



#=======================================================================================================================================
#                Load Dataset and Helping Function 
#=======================================================================================================================================

def colorContinent(row):
    if row['continent'] == ('Europe'): return 'green'
    if row['continent'] == ('Asia'): return 'yellow'
    if row['continent'] == ('North America'): return 'blue'
    if row['continent'] == ('South America'): return 'blue'
    if row['continent'] == ('Africa'): return 'brown'
    if row['continent'] == ('Oceania'): return 'purple'

def filterResults(lowerDate, higherDate, filterColumn):
    higherDateSplit = higherDate.split("-")
    lastDayInMonth = calendar.monthrange(int(higherDateSplit[0]), int(higherDateSplit[1]))[1]
    lowerDateFilter = dfFilter[dfFilter['date'] >= '{}-01'.format(lowerDate)]
    higherDateFilter = dfFilter[dfFilter['date'] <= '{}-{}'.format(higherDate, lastDayInMonth)]
    
    filterDF = dfFilter[dfFilter.index.isin(lowerDateFilter.index)]
    filterDF = filterDF[filterDF.index.isin(higherDateFilter.index)]
    return filterDF.groupby(['location', 'year', 'month'])[filterColumn].agg({'sum'}).reset_index().groupby(['location'])['sum'].agg({'sum'}).reset_index()


dictTime = {'1': {'label' : '2020/01'},
            '2': {'label' : '2020/02'},
            '3': {'label' : '2020/03'},
            '4': {'label' : '2020/04'},
            '5': {'label' : '2020/05'},
            '6': {'label' : '2020/06'},
            '7': {'label' : '2020/07'},
            '8': {'label' : '2020/08'},
            '9': {'label' : '2020/09'},
            '10': {'label' : '2020/10'},
            '11': {'label' : '2020/11'},
            '12': {'label' : '2020/12'},
            '13': {'label' : '2021/01'},
            '14': {'label' : '2021/02'},
            '15': {'label' : '2021/03'}}

dictMapperFilter = {1: '2020-01',
                    2: '2020-02',
                    3: '2020-03',
                    4: '2020-04',
                    5: '2020-05',
                    6: '2020-06',
                    7: '2020-07',
                    8: '2020-08',
                    9: '2020-09',
                    10: '2020-10',
                    11: '2020-11',
                    12: '2020-12',
                    13: '2021-01',
                    14: '2021-02',
                    15: '2021-03'}

#path = 'C:/Users/Jorge/Documents/Mestrado/2Semestre/Data Visualization/Projeto/'
path = ''

mapPicklistOptions = ['new_cases', 'new_cases_per_million']
mapPicklistOptions = [dict(label=gas.replace('_', ' '), value=gas) for gas in mapPicklistOptions]

df = pd.read_csv(path + 'owid-covid-data.csv')
gdpDf = pd.read_csv(path + 'GDP.csv')
img = base64.b64encode(open(path + 'title.png', 'rb').read())

#=======================================================================================================================================
#                Preparing the Data
#=======================================================================================================================================

dfFilter = pd.DataFrame(df[['location', 'total_cases', 'new_cases', 'date', 'new_cases_per_million', 'new_tests', 'continent', 'gdp_per_capita', 'new_vaccinations_smoothed']])
dfFilter = dfFilter[~dfFilter.location.str.contains('World')]
dfFilter['year'] = pd.DatetimeIndex(dfFilter['date']).year
dfFilter['month'] = pd.DatetimeIndex(dfFilter['date']).month

#====================================================================

dfWorldData = filterResults(dictMapperFilter.get(1), dictMapperFilter.get(15), 'new_cases')

#====================================================================

dfContinentNewCases = dfFilter.groupby(['continent', 'year', 'month'])['new_cases'].agg({'sum'}).reset_index()

dfContinentNewCases['date'] = dfContinentNewCases.apply (lambda row: str(row['year']) + '-' + str(row['month']), axis=1)

continents = list(dfContinentNewCases['continent'].unique())

indexData = list(dfContinentNewCases['date'].unique())
indexData = [indexData[-1]] + indexData[:-1]

dfContinent = pd.DataFrame(columns=continents, index = indexData)

for index, row in dfContinentNewCases.iterrows():
    dfContinent.loc[row['date'], row['continent']] = row['sum']
dfContinent = dfContinent.fillna(0)

#====================================================================

dfCountryChoosen = pd.DataFrame(dfFilter[['location', 'continent']])
dfCountryChoosen['pick'] = 0
dfCountryChoosen = dfCountryChoosen.drop_duplicates(subset=['location']).dropna().reset_index(drop=True)

countryIdx = dfCountryChoosen.index[dfCountryChoosen['location'] == 'Portugal'].tolist()[0]
dfCountryChoosen.at[countryIdx, 'pick'] = 1

countryList = [dict(label=gas, value=gas) for gas in dfCountryChoosen['location']]

#====================================================================

dfVacc = dfFilter
dfVacc = dfVacc.groupby(['continent', 'year', 'month'])['new_vaccinations_smoothed'].agg({'sum'}).reset_index()

dfVacc['date'] = dfVacc.apply (lambda row: str(row['year']) + '-' + str(row['month']), axis=1)

indexDataVacc = list(dfVacc['date'].unique())
indexDataVacc = [indexDataVacc[-1]] + indexDataVacc[:-1]

dfVaccFinal = pd.DataFrame(columns = continents, index = indexDataVacc)

for index, row in dfVacc.iterrows():
    dfVaccFinal.loc[row['date'], row['continent']] = row['sum']
dfVaccFinal = dfVaccFinal.fillna(0)
dfVaccFinal = dfVaccFinal.iloc[11:]

#====================================================================

countryInd = dfFilter.loc[dfFilter['location'].str.contains('Portugal')]
countryInd.loc[countryInd[countryInd['new_cases'] < 0].index, 'new_cases'] = 0


#=======================================================================================================================================
#                Building Graphs
#=======================================================================================================================================

data1  =  dict(type = 'choropleth',
              locations = dfWorldData['location'],  #There are three ways to 'merge' your data with the data pre embedded in the map
              locationmode = 'country names',
              z = round(dfWorldData['sum'], 3),
              colorscale = 'emrld',
              colorbar = dict(title = 'Covid cases', bgcolor  =  'white'),
              #hovertemplate = 'z:%{}' #'dfWorldData['sum']'
             )

layout1  =  dict(geo = dict(scope = 'world',
                            projection = dict(type = 'natural earth'),
                            #showland = True,   # default  =  True
                            landcolor = 'black',
                            lakecolor = 'white',
                            showocean = True,
                            oceancolor = 'LightCyan',
                            #bgcolor = 'rgb(173,195,193)',
                            ),
                         
                title = dict(text = 'Impact of Covid-19 in the World', x = .48, y = 0.91),
                height = 800,
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'
                )

fig1 = go.Figure(data = data1, layout = layout1)

#====================================================================

continentVacc1 = dict(type='scatter',y=dfVaccFinal['Africa'],x=dfVaccFinal.index,name='Africa')

continentVacc2 = dict(type='scatter', y=dfVaccFinal['Asia'], x=dfVaccFinal.index, name='Asia')

continentVacc3 = dict(type='scatter', y=dfVaccFinal['Europe'], x=dfVaccFinal.index, name='Europe')

continentVacc4 = dict(type='scatter', y=dfVaccFinal['North America'], x=dfVaccFinal.index, name='North America')

continentVacc5 = dict(type='scatter', y=dfVaccFinal['South America'], x=dfVaccFinal.index, name='South America')

continentVacc6 = dict(type='scatter', y=dfVaccFinal['Oceania'], x=dfVaccFinal.index, name='Oceania')


data2 = [continentVacc1, continentVacc2, continentVacc3, continentVacc4, continentVacc5, continentVacc6]

layout2 = dict(title=dict(text='Total vaccination per month'),
               xaxis=dict(title='Timeline'),
               yaxis=dict(title='Number of vaccinations'),
               paper_bgcolor = 'rgba(0,0,0,0)',
               plot_bgcolor = 'rgba(0,0,0,0)')

fig2 = go.Figure(data = data2, layout = layout2)

#====================================================================

data3 = dict(type = 'bar', x = gdpDf['Continent'], y = gdpDf['GDP(US$billion)'])

layout3 = dict(title = dict(text = 'GDP per Continent'),
               yaxis=dict(title='GDP (US$)'),
               xaxis=dict(title='Continents'),
               paper_bgcolor = 'rgba(0,0,0,0)',
               plot_bgcolor = 'rgba(0,0,0,0)',
               colorway  =  ['rgb(65,146,128)'])

fig3 = go.Figure(data = data3, layout = layout3)

#====================================================================

continent1 = dict(type='scatter',y=dfContinent['Africa'],x=dfContinent.index,name='Africa')

continent2 = dict(type='scatter', y=dfContinent['Asia'], x=dfContinent.index, name='Asia')

continent3 = dict(type='scatter', y=dfContinent['Europe'], x=dfContinent.index, name='Europe')

continent4 = dict(type='scatter', y=dfContinent['North America'], x=dfContinent.index, name='North America')

continent5 = dict(type='scatter', y=dfContinent['South America'], x=dfContinent.index, name='South America')

continent6 = dict(type='scatter', y=dfContinent['Oceania'], x=dfContinent.index, name='Oceania')


data4 = [continent1, continent2, continent3, continent4, continent5, continent6]

layout4 = dict(title = dict(text = 'Covid-19 new cases per month'),
			   xaxis = dict(title = 'Timeline'),
			   yaxis = dict(title = 'New cases of Covid-19'),
               paper_bgcolor = 'rgba(0,0,0,0)',
               plot_bgcolor = 'rgba(0,0,0,0)')
                 
fig4 = go.Figure(data = data4, layout = layout4)

#====================================================================

data5  =  dict(type = 'choropleth',
              locations = dfCountryChoosen['location'],  #There are three ways to 'merge' your data with the data pre embedded in the map
              locationmode = 'country names',
              z = dfCountryChoosen['pick'],
              colorscale = 'emrld'
             )

layout5  =  dict(geo = dict(scope = 'europe',
                            projection = dict(type = 'natural earth'),
                            #showland = True,   # default  =  True
                            landcolor = 'black',
                            lakecolor = 'white',
                            showocean = False,
                            #bgcolor = 'rgb(173,195,193)',
                            visible= False,
                            ),
                title = dict(text = 'Geolocation', x = .15, y = 0.91),         
                height = 450,
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'
                )

fig5 = go.Figure(data = data5, layout = layout5)

#====================================================================

infoInd = dict(type='scatter',y=countryInd['new_cases'], x=countryInd['date'], name='Portugal')

dataInd = [infoInd]
layoutInd = dict(title=dict(text='New Covid-19 cases per day'),
                 xaxis=dict(title='Timeline'),
                 yaxis=dict(title='New cases of Covid-19'),
                 paper_bgcolor = 'rgba(0,0,0,0)',
                 plot_bgcolor = 'rgba(0,0,0,0)',
                 colorway  =  ['rgb(65,146,128)']
                 )

figInd = go.Figure(data=dataInd, layout=layoutInd)


#=======================================================================================================================================
#                App
#=======================================================================================================================================

app = dash.Dash(__name__)

server = app.server

app.title = 'A Shot of Data | DV Group AM'

app.layout = html.Div(children=[
    
    html.Div([
            html.Div([
                    #html.Div('Covid-19       The time with us', style = {'font-size':'70px', 'text-align': 'center'}),
                    html.Img(src='data:image/png;base64,{}'.format(img.decode())),
                
                     html.Div(
                         html.Div('End of 2019, the world was preparing for a fresh start - a new year, preparing trips and plans for the future with the idea that this was going to be another typical year, then… one article referring to a new type of virus attacking Wuhan, China appeared. One article after the another started to fill the news, announcing the terrifying numbers of infected people and deaths. Everyone had the impression that it would only affect the city where it was. Suddenly, new cases were appearing in neighbor countries. This small problem started to escalate quickly due to the quick proliferation of the virus. Italy, Spain, United States of America, all of them felt the lack of control and impact that the Coronavirus started to have on their population. At some point all of us faced this problem. On March 11, 2020 while everyone started to be advised to lock up themselves in their homes for safety, the World Health Organization declare this quick spread of virus called Covid-19 has a ‘Pandemic’, the first of its kind for many generations. This new status caught all world population by surprise and led to total chaos in some countries. We can visualize the impact of Covid-19 around the world in given periods of time to help us having a notion of the outbreak.',
                                  style = {'text-align': 'top'})
                         , style = {'border-radius': '10px', 'background-color': 'white', 'display': 'inline-block', 'padding': '20px', 'box-shadow': '5px 5px 10px #888888', 'margin-top': '5%', 'position':'relative', 'flex-grow': '1'}),

                ], style = {'width' : '23%', 'display': 'flex', 'flex-direction': 'column'}),
            
            
            html.Div(
        html.Div([
            html.Div([
                html.Div(
                    dcc.Dropdown(id = 'picklistValue',
                                 options = mapPicklistOptions,
                                 ), style = {'display': 'inline-block', 'width':'18%', 'margin-left': '5%', 'color':'black'}),
        
                 html.Div(
                         dcc.RangeSlider(
                             id = 'yearSlider',
                             min = 1,
                             max = 15,
                             value = [1, 15],
                             marks  =  dictTime,
                             step = 1), style = {'margin-left': '5%', 'margin-right': '2%', 'display': 'inline-block', 'width':'67%', 'height':'120%'})
            ], style = {'height':'25px', 'padding-top':'20px'}),
            
            html.Div(
                    dcc.Graph(
                            id = 'worldGraph',
                            figure = fig1)),
        ],style = {'border-radius': '10px', 'background-color': 'white', 'box-shadow': '5px 5px 10px #888888'}), style = {'padding-left':'2%', 'width':'75%', 'display': 'inline-block', 'vertical-align': 'top'}),
         ], style = {'padding':'30px 5% 30px 5%', 'display': 'flex'}),


        html.Div([
            html.Div([
                    html.Div('Spread of an invisible enemy', style  =  {'padding-bottom':'20px', 'font-weight': 'bold', 'font-size': '22px'}),
            
                    html.Div('To block the spread of the disease, governments started to close the connections to other countries, with imposed lockdowns tried to win the fight with the virus. Every day, we could see in the news the numbers rise, from little countries to the biggest ones. Infections, recoveries, deaths, this was the only topic that entire nations wanted to know. But being on the modern days, with advanced science, technology, the only thing that everyone was begging was for a miracle to fight it. The first estimation of a vaccine was forecasted to appear only within 10 years. What could we do until then? Since modern problems require modern solutions, laboratories started to study fiercely the virus while Data Scientist studied how to stop the spread and to help governments to impose new restrictions. Breakthrough discoveries were done every single day in all areas having all the same goal - stop this global pandemic . In the middle of 2020, the cases skyrocket to new heights. The initial phase of the pandemic started to appear as a sea of roses comparing to what we where facing at that moment. New measures were taken thanks to a second wave. But in the end of this atypical year, we took a fresh breath, and societies started to gain some life, but why? Could it only be happenning because of the strict measures imposed to us? Were we finally starting to have group immunity? What could explain the sudden drop of new cases in the beginning of 2021?'),
                ], style  =  {'display': 'inline-block', 'width':'40%', 'vertical-align':'top', 'border-radius': '10px', 'background-color': 'white', 'padding': '20px', 'box-shadow': '5px 5px 10px #888888'}),
            
            html.Div([
                    html.Div(
            		         dcc.Graph(
                			         id = 'continentCasesGraph',
                			         figure = fig4
            		          ))
                ], style = {'display': 'inline-block', 'width':'56.7%', 'border-radius': '10px', 'background-color': 'white', 'margin-left': '2%', 'box-shadow': '5px 5px 10px #888888'})            
            ], style  =  {'padding':'30px 5% 30px 5%', 'display': 'flex'}),

    html.Div([
        html.Div([
                    html.Div([
                        html.Div('A shot of hope', style  =  {'font-weight': 'bold', 'font-size': '22px'}),
        
                        html.Div('For the surprise of humankind, vaccines were developed throughout the year of 2020. It started to be tested and consequently approved by EMA, FDA etc.. This new hope in bottles led countries bidding and buying a lot of batches to start vaccination in the respective countries. It is visible that some continents were more affected than others and the rush to vaccinate on those began. One scenario raised by experts was that the continents with more economical power would for sure buy and vaccinate more. Would these continents be incorruptible enough to buy the right amount for necessity or just to impose their economical power? We can visualize that Asia, North America and Europe are the continents with higher number of vaccinations. It is possible to observe that these specific continents are the most affected by the pandemic, therefore is safe to say that all the money invested would be for the benefit of the population in these countries and continents.',
                                style  =  {'padding-top':'20px'}),
                        
                        ],style = {'border-radius': '10px', 'background-color': 'white', 'padding': '20px', 'box-shadow': '5px 5px 10px #888888', 'height': '410px', 'width':'30%', 'vertical-align': 'top', 'position':'relative', 'flex-grow': '1'}),
                    

        
        
                html.Div([
                    html.Div(
        		       dcc.Graph(
            		   id = 'countryGDPperNewCases',
            		   figure = fig2
        		    ), style = {'border-radius': '10px', 'background-color': 'white', 'box-shadow': '5px 5px 10px #888888'}),
                ], style = {'display': 'inline-block', 'width':'37%', 'padding-left':'2%', 'vertical-align': 'top'}),
    	
        
        html.Div([
            html.Div(
                dcc.Graph(                
            		id = 'meanGDP',
                	figure = fig3
            	), style = {'border-radius': '10px', 'background-color': 'white', 'box-shadow': '5px 5px 10px #888888'}),
            
            ], style = {'display': 'inline-block', 'width':'29%', 'padding-left':'2%', 'vertical-align': 'top'}),
        ], style  =  {'padding':'30px 5% 30px 5%', 'display': 'flex'})]),



    html.Div([
        html.Div([
            html.Div([
                html.Div('At this point in time', style  =  {'padding-bottom':'20px', 'display': 'inline-block', 'padding-top':'10px', 'font-weight': 'bold', 'font-size': '22px'}),
                
                html.Div(
                        dcc.Dropdown(id = 'picks1',
                                     options = countryList,
                        ), style = {'display': 'inline-block', 'width':'48%', 'margin-left': '4%', 'vertical-align': 'top', 'color' : 'black', 'box-shadow': '5px 5px 10px #888888', 'float': 'right'})
                ]),
            
            
                html.Div('Many debates and discussions where taken around this topic. There were a lot of possible points of view and they normally change from country to country. This is given by the fact that the ways governments fight against the virus and the actions that were taken to insure the well-being of the population also affect vaccination efficiency. Even  being the pandemic a global topic, every single country has their own history with Covid-19.',
                         style  =  {'margin-top': '2%'}),
                
                html.Div('Feel free to explore and to see how the Covid impacted each country.',
                         style  =  {'margin-top': '12%'}),
        
        
            ], style = {'width':'25%', 'border-radius': '10px', 'background-color': 'white', 'padding': '20px', 'box-shadow': '5px 5px 10px #888888'}),
        
        html.Div([        
        html.Div([
            html.Div(
                dcc.Graph(
                 id = 'worldGraph11',
                 figure = fig5)
            , style = {'width':'70%'})
            ], style = {'padding-right': '2%'}),
        
        html.Div([
                dcc.Graph(
                			id = 'continentCasesGraph1',
                			figure = figInd
            		)
            ], style = {'vertical-align':'top', 'margin-left': '2%'}),
        
        ], style = {'background-color': 'white', 'box-shadow': '5px 5px 10px #888888','border-radius': '10px', 'display': 'inline-flex', 'margin-left': '2%', 'padding-right': '20px'})

        ], style  =  {'padding':'30px 5% 30px 5%', 'display': 'flex'}),


        html.Div('Jorge Pereira - 20201085 | Felipe Costa - 20201041 | Fábio Lopes - 20200597', style = {'color': 'white', 'display': 'flex', 'justify-content': 'center', 'padding-bottom': '10px'})
    
    
], style = {'background': 'linear-gradient(to right, #303030, #808080)','font-family': 'Arial, Helvetica, sans-serif', 'font-size':'16px', 'text-align': 'justify', 'line-height': '23px'})


#=======================================================================================================================================
#                Callback functions
#=======================================================================================================================================
             
@app.callback(
    Output('worldGraph', 'figure'),
    [Input('yearSlider', 'value'),
     Input('picklistValue', 'value')]
)
def updateWorldMap(filterDate, picklistOption):
    if(picklistOption == None):
        picklistOption = 'new_cases'
    
    minFilter = dictMapperFilter.get(filterDate[0])
    maxFilter = dictMapperFilter.get(filterDate[1])
    
    dfWorldData = filterResults(minFilter, maxFilter, picklistOption)
     
    data1 = dict(type = 'choropleth',
				locations = dfWorldData['location'],
				locationmode = 'country names',
				z = round(dfWorldData['sum'], 3),
				colorscale = 'emrld',
				colorbar = dict(title = 'Covid cases')
                )
    
    fig = go.Figure(data = data1, layout = layout1)
    return fig

#====================================================================

@app.callback(
    Output('worldGraph11', 'figure'),
    Output('continentCasesGraph1', 'figure'),
    [Input('picks1', 'value')]
)
def updateCountryChoosen(picklistOption):    
    countryInd = dfFilter.loc[dfFilter['location'].str.contains(picklistOption)]
    countryInd.loc[countryInd[countryInd['new_cases'] < 0].index, 'new_cases'] = 0
    
    dfCountryChoosen['pick'] = 0
    countryIdx = dfCountryChoosen.index[dfCountryChoosen['location'] == picklistOption].tolist()[0]
    dfCountryChoosen.at[countryIdx, 'pick'] = 1
     
    dataInfo  =  dict(type = 'choropleth',
              locations = dfCountryChoosen['location'],
              locationmode = 'country names',
              z = dfCountryChoosen['pick'],
              colorscale = 'emrld'
             )

    layoutInfo  =  dict(geo = dict(scope = dfCountryChoosen.loc[countryIdx]['continent'].lower(),
                            projection = dict(type = 'natural earth'),
                            landcolor = 'black',
                            lakecolor = 'white',
                            showocean = False,
                            visible= False
                            ),
                title = dict(text = 'Geolocation', x = .15, y = 0.91),         
                height = 450,
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'
                )

    fig = go.Figure(data = dataInfo, layout = layoutInfo)
    
    
    infoInd = dict(type='scatter',y=countryInd['new_cases'], x=countryInd['date'], name=picklistOption)

    dataInd = [infoInd]
    layoutInd = dict(title=dict(text='Covid-19 cases per month'),
                     xaxis=dict(title='Months'),
                     yaxis=dict(title='New cases of Covid-19'),
                     paper_bgcolor = 'rgba(0,0,0,0)',
                     plot_bgcolor = 'rgba(0,0,0,0)',
                     colorway  =  ['rgb(65,146,128)']
                     )

    fig2 = go.Figure(data=dataInd, layout=layoutInd)
    
    return fig, fig2

#====================================================================

if __name__ == '__main__':
    app.run_server(debug = False)
