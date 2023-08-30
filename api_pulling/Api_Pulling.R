# Load libraries 'jsonlite' and 'httr'
library(jsonlite)
library(httr)

# Use GET() function and specify API's URL
res = GET("https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/911_Calls_New/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson")

# Use rawTOChar() function to convert raw code into a character vector in JSON format
rawToChar(res$content)

# Use rawToChar() function inside of fromJSON() function to format data for R
data = fromJSON(rawToChar(res$content), flatten= T)
names(data)

# Use $ operator to look at the 'features' dataframe
data$features

# View observations from 'features' dataframe
View(data$features)
