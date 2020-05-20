def tripDistribution(tripGeneration, costMatrix):
    costMatrix['ozone'] = costMatrix.columns
    costMatrix = costMatrix.melt(id_vars=['ozone'])
    costMatrix.columns = ['ozone', 'dzone', 'total']
    production = tripGeneration['Production']
    production.index.name = 'ozone'
    attraction = tripGeneration['Attraction']
    attraction.index.name = 'dzone'
    aggregates = [production, attraction]
    dimensions = [['ozone'], ['dzone']]
    IPF = ipfn.ipfn(costMatrix, aggregates, dimensions)
    trips = IPF.iteration()
    return(trips.pivot(index='ozone', columns='dzone', values='total'))
