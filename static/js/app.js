let articles = [];
let currentArticle = 0;
let weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function updateDateTime() {
    let now = new Date()
    let dateBox = document.getElementById('date')
    let timeBox = document.getElementById('time')
    dateBox.innerText = now.toLocaleDateString('en-us', {weekday:'short', day: 'numeric', month:'long'})
    timeBox.innerText = now.toLocaleTimeString('en-us', {hour: 'numeric', minute: '2-digit'});
}

function updateNewsData() {
    return new Promise((resolve, reject) => {
        d3.json('/news').then(function(data) {
            console.log(data)

            articles = data.articles;
            resolve(1);
        })

    })
    let out = new Promise()
    return out;
}

async function updateNewsDisplay() {
    if (articles.length > 0) {
        currentArticle = (currentArticle + 1) % articles.length;
        d = articles[currentArticle];

        var img = new Image();
        img.src = d.urlToImage;

        // get new image in background
        // fade out current story
        // after fade completed, change text
        // after fade completed, text changed, and image finishes loading, then fade back in.

        let news = document.querySelector('#news')

        news.style.opacity = 0;
        function fadeOut() {
            return new Promise((resolve, reject) => {
                let anim = news.animate([{opacity: 1}, {opacity: 0}], {duration: 750})
                anim.onfinish = () => resolve(1);
            })
        }

        function fadeIn() {
            return new Promise((resolve, reject) => {
                let anim = news.animate([{opacity: 0}, {opacity: 1}], {duration: 750})
                anim.onfinish = () => resolve(1);
            })
        }

        function loadImage(url, elem) {
            return new Promise((resolve, reject) => {
                elem.onload = () => resolve(elem);
                elem.onerror = reject;
                elem.src = url;
            });
        }

        fadeOut().then(() => {
            newsImg = document.querySelector('#news>img')
            document.querySelector('#news>p').innerText = d.title;
            return loadImage(d.urlToImage, newsImg)
        }).catch(() => {
            newsImg = document.querySelector('#news>img')
            return loadImage('/static/img/news.png', newsImg)
        }).then(() => {
            news.style.opacity = 1;
            return fadeIn;
        })

        // fadeOut.finished.then(() => {
        //     newsImg = document.querySelector('#news>img')
        //     document.querySelector('#news>p').innerText = d.title;
        //     return loadImage(d.urlToImage, newsImg)
        // }).catch(() => {
        //     newsImg = document.querySelector('#news>img')
        //     return loadImage('/static/img/news.png', newsImg)
        // }).then(() => {
        //     news.style.opacity = 1;
        //     let fadeIn = news.animate([{opacity: 0}, {opacity: 1}], {duration: 750})
        //     return fadeIn.finished;
        // })
    }
}

function updateWeather() {
    d3.json('/weather').then(function(data) {
        console.log(data)

        var sunrise = new Date(data.current.sunrise*1000).toLocaleTimeString('en-us', {hour: 'numeric', minute: '2-digit'});
        var sunset = new Date(data.current.sunset*1000).toLocaleTimeString('en-us', {hour: 'numeric', minute: '2-digit'});

        d3.select('#sunrise-sunset').html(`<img src='/static/img/sunrise.png'> ${sunrise} <img src='/static/img/sunset.png'> ${sunset}`)

        var moonDiameter = 30
        phase = SunCalc.getMoonIllumination(now).phase

        var moonSvg = d3.select('#sunrise-sunset').append('svg')
            .attr('width', moonDiameter)
            .attr('height', moonDiameter)

        moonSvg.html('')

        moonSvg.append('circle')
            .attr('cx', 0.5*moonDiameter)
            .attr('cy', 0.5*moonDiameter)
            .attr('r', 0.5*moonDiameter)
            .attr('fill', '#DDD')

        moonSvg.append('path')
            .attr('d', d => `M0 ${-0.5*moonDiameter}` + 
                            `c${(2*phase % 1 - 0.5) * moonDiameter * 4/3} 0, ${(2*phase % 1 - 0.5) * moonDiameter * 4/3} ${moonDiameter}, 0 ${moonDiameter} ` +
                            `c${(phase > 0.5 ? -1 : 1) * moonDiameter * 2/3} 0, ${(phase > 0.5 ? -1 : 1) * moonDiameter * 2/3} ${-moonDiameter}, 0 ${-moonDiameter}`)
            .attr('transform', `translate(${0.5*moonDiameter},${0.5*moonDiameter})`)
            .attr('fill', '#222')

        d3.select('#current-temperature').text(`${Math.round(data.current.temp)}°`)

        d3.select('#current').select('#current-other').select("img")
            .attr('src', `http://openweathermap.org/img/wn/${data.current.weather[0].icon}.png`)

        d3.select('#current').select('#current-other').select("#humidity")
            .text(`${data.current.humidity}%`)

        let precipColor = x => {
            if (x == 0) return "#444444";
            else if (x < 2) return "#00BB11";
            else if (x < 10) return "#FFDD00";
            else if (x < 50) return "#FF0000";
            else return "#FF00FF";
        }

        let minuteData = data.minutely.map((x, i) => {return {startAngle: i * Math.PI / 30, endAngle: (i + 1) * Math.PI / 30 + .01, color: precipColor(x.precipitation)}})

        let minuteForecast = d3.select('#minute-forecast').selectAll('.arc').data(minuteData, (d, i) => i)

        let arc = d3.arc()
            .innerRadius(65)
            .outerRadius(75)

        minuteForecast.enter()
            .append('path')
            .classed('arc', true)
            .attr('d', arc)
            .merge(minuteForecast)
            .style('fill', d => d.color)
            .attr('transform', 'translate(75,75)')

        let forecasts = d3.select('#forecast').selectAll('.forecast').data(data.daily.slice(0, 3))

        forecasts.enter().append('p')
            .attr('class', 'forecast')
            .merge(forecasts)
            .html(d => `<span class='weekday'>${weekdays[new Date(d.dt*1000).getDay()]}</span> <span class='forecast-description'>${Math.round(d.temp.min)}° - ${Math.round(d.temp.max)}° ${d.weather[0].description}</span>`)
            .append('img').attr('src', d => `http://openweathermap.org/img/wn/${d.weather[0].icon}.png`)
            .attr('width', '30px')
            .attr('height', '30px')
        
        forecasts.exit().remove();

    })
}

function updateMilkyWay() {
    latitude = 30.44422
    longitude = -97.77187

    now = new Date()
    yesterday = new Date()
    yesterday.setDate(now.getDate() - 1)
    yesterday.setHours(12,0,0)
    today = new Date()
    today.setHours(12,0,0)
    tomorrow = new Date()
    tomorrow.setDate(now.getDate() + 1)
    tomorrow.setHours(12,0,0)

    let startTime = new Date()
    startTime.setMinutes(Math.floor(startTime.getMinutes() / 15)*15, 0)
    let endTime = new Date()
    endTime.setHours(12, 0, 0)
    endTime.setDate(endTime.getDate() + 1)

    sunTimes = [yesterday, today, tomorrow].map(x => SunCalc.getTimes(x, latitude, longitude))
    moonTimes = [yesterday, today, tomorrow].map(x => SunCalc.getMoonTimes(x, latitude, longitude))
    galacticCenterTimes = [yesterday, today, tomorrow].map(x => SunCalc.getGalacticCenterTimes(x, latitude, longitude))

    moonTimes = []
    sunTimes = []
    gcTimes = []

    for (let i = -1; i <= 2; i++) {
        day = new Date()
        day.setDate(today.getDate() + i)
        day.setHours(12, 0, 0)
        moonTimes.push(SunCalc.getMoonTimes(day, latitude, longitude))
        //sunTime = SunCalc.getTimes(day, latitude, longitude)
        //sunTimes.push({'night': sunTime.night, 'nightEnd':sunTime.nightEnd})
        sunTimes.push(SunCalc.getTimes(day, latitude, longitude))
        gcTimes.push(SunCalc.getGalacticCenterTimes(day, latitude, longitude))
    }

    flatMoonTimes = [].concat.apply([], moonTimes.map(x => Object.entries(x))).map(x => {return {'time':x[1], 'type':x[0]}; }).sort((a, b) => a.time.valueOf() - b.time.valueOf())
    flatSunTimes = [].concat.apply([], sunTimes.map(x => Object.entries(x))).map(x => {return {'time':x[1], 'type':x[0]}; }).sort((a, b) => a.time.valueOf() - b.time.valueOf())
    flatGCTimes = [].concat.apply([], gcTimes.map(x => Object.entries(x))).map(x => {return {'time':x[1], 'type':x[0]}; }).sort((a, b) => a.time.valueOf() - b.time.valueOf())

    sunBlockTimes = []

    for (let i = 0; i < flatSunTimes.length - 1; i++) {
        let block = [flatSunTimes[i], flatSunTimes[i+1]]
        if (flatSunTimes[i].time < endTime) sunBlockTimes.push(block);
    }



    let height = 100;
    let width = 480;
    let galaxyLineRadius = 1000
    let moonDiameter = 12

    let margin = {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
    }

    let chartHeight = height - margin.top - margin.bottom;
    let chartWidth = width - margin.left - margin.right;

    const svg = d3.select("#milky-way").select('svg')
        .attr('height', height)
        .attr('width', width)

    svg.html('')

    const mask = svg.append('mask')
        .attr('id', 'chartMask')
        .append('rect')
        .attr('width', chartWidth)
        .attr('height', chartHeight)
        .attr('fill', 'white')

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

    const maskedG = svg.append('g')
        .attr('mask', 'url(#chartMask)')
        .attr('transform', `translate(${margin.left},${margin.top})`)

    xScale = d3.scaleTime().domain([startTime, endTime]).range([0, chartWidth])
    yScale = d3.scaleLinear().domain([0, Math.PI/2]).range([chartHeight, 0])

    // xAxis = d3.axisBottom(xScale)

    skyColors = {
        'nightSky': '#000026',
        'darkSky' : '#2c0b4d',
        'twilight': '#733973',
        'riseSet': '#b35071',
        'goldenHour': '#ffcc73',
        'daySky': '#ffff73'
    }

    gcColors = {
        'nightSky': '#f1ebd3',
        'darkSky' : '#7b6583',
        'twilight': '#8c5d86',
        'riseSet': '#b9607b',
        'goldenHour': '#febe7d',
        'daySky': '#ffff73'
    }

    sunColor = {
        'nadir': skyColors.nightSky,
        'nightEnd': skyColors.darkSky,
        'nauticalDawn': skyColors.twilight,
        'dawn': skyColors.riseSet,
        'sunrise': skyColors.riseSet,
        'sunriseEnd': skyColors.goldenHour,
        'goldenHourEnd': skyColors.daySky,

        'solarNoon': skyColors.daySky,
        'goldenHour': skyColors.goldenHour,
        'sunsetStart': skyColors.riseSet,
        'sunset': skyColors.riseSet,
        'dusk': skyColors.twilight,
        'nauticalDusk': skyColors.darkSky,
        'night': skyColors.nightSky
    }

    function gcColor(time) {
        let sunTimes = flatSunTimes.filter(x => x.time < time)
        let type = sunTimes[sunTimes.length - 1].type

        let colorTypes = {
            'nadir': gcColors.nightSky,
            'nightEnd': gcColors.darkSky,
            'nauticalDawn': gcColors.twilight,
            'dawn': gcColors.riseSet,
            'sunrise': gcColors.riseSet,
            'sunriseEnd': gcColors.goldenHour,
            'goldenHourEnd': gcColors.daySky,

            'solarNoon': gcColors.daySky,
            'goldenHour': gcColors.goldenHour,
            'sunsetStart': gcColors.riseSet,
            'sunset': gcColors.riseSet,
            'dusk': gcColors.twilight,
            'nauticalDusk': gcColors.darkSky,
            'night': gcColors.nightSky
        }

        return colorTypes[type]
    }

    sunBlocks = maskedG.selectAll('.sunBlock').data(sunBlockTimes)
        .enter()
        .append('rect')
        .attr('x', d => Math.floor(xScale(d[0].time)))
        .attr('y', 0)
        .attr('width', d => Math.ceil(xScale(Math.min(d[1].time, endTime)) - xScale(Math.min(d[0].time))))
        .attr('height', chartHeight)
        .attr('fill', d => sunColor[d[0].type])
        // .attr('fill', 'black')


    // g.append('g')
    // .attr('class', 'x-axis')
    // .attr('transform', `translate(0, ${chartHeight})`)
    // .call(xAxis)


    let moonPositions = []
    let gcPositions = []

    for (let i = 0; i < endTime.valueOf() - startTime.valueOf(); i += (endTime.valueOf() - startTime.valueOf())/30) {
        let time = new Date(startTime.valueOf() + i )
        // let position = SunCalc.getGCPosition(time, latitude, longitude)
        let position0 = SunCalc.getStarPosition(time, latitude, longitude, (17 + 47/60 + 58.9/3600), -(28 + 4/60  + 53/3600))
        let position =  SunCalc.getStarPosition(time, latitude, longitude, (17 + 45/60 + 37.2/3600), -(28 + 56/60 + 10/3600))
        let position1 = SunCalc.getStarPosition(time, latitude, longitude, (17 + 43/60 + 13.1/3600), -(29 + 47/60 + 18/3600))
        let result = {}
        result.time = time
        result.position0 = position0
        result.position = position
        result.position1 = position1
        if (position.altitude > 0) gcPositions.push(result)
        
        let moonPosition = SunCalc.getMoonPosition(time, latitude, longitude)
        moonPosition.time = time
        if (moonPosition.altitude > 0) moonPositions.push(moonPosition)
    }


    maskedG.selectAll('.gcPosition').data(gcPositions)
        .enter()
    .append('line')
        .attr('x1', d => xScale(d.time) + galaxyLineRadius*(d.position0.azimuth - d.position1.azimuth))
        .attr('x2', d => xScale(d.time) - galaxyLineRadius*(d.position0.azimuth - d.position1.azimuth))
        // .attr('x2', d => xScale(d.time) + 5)
        .attr('y1', d => yScale(d.position0.altitude) - galaxyLineRadius*(d.position0.altitude - d.position1.altitude))
        .attr('y2', d => yScale(d.position1.altitude) + galaxyLineRadius*(d.position0.altitude - d.position1.altitude))
        // .attr('y2', d => yScale(d.position1.altitude))
        .attr('stroke', d => gcColor(d.time))

    maskedG.selectAll('.gcPosition').data(gcPositions)
        .enter()
    .append('circle')
        .attr('cx', d => xScale(d.time))
        .attr('cy', d => yScale(d.position.altitude))
        .attr('r', 2)
        .attr('fill', d => gcColor(d.time))


    phase = SunCalc.getMoonIllumination(now).phase

    maskedG.selectAll('.moonPosition').data(moonPositions)
        .enter()
    .append('circle')
        .attr('cx', d => xScale(d.time))
        .attr('cy', d => yScale(d.altitude))
        .attr('r', 0.5*moonDiameter)
        .attr('fill', '#DDD')

    maskedG.selectAll('.moonPosition').data(moonPositions)
        .enter()
    .append('path')
        .attr('d', d => `M0 ${-0.5*moonDiameter} c${(2*phase % 1 - 0.5) * moonDiameter * 4/3} 0, ${(2*phase % 1 - 0.5) * moonDiameter * 4/3} ${moonDiameter}, 0 ${moonDiameter} c${(phase > 0.5 ? -1 : 1) * moonDiameter * 2/3} 0, ${(phase > 0.5 ? -1 : 1) * moonDiameter * 2/3} ${-moonDiameter}, 0 ${-moonDiameter}`)
        .attr('transform', d => `translate(${xScale(d.time)},${yScale(d.altitude)})`)
        .attr('fill', '#222')
}

function updatePollen() {
    d3.json('/pollen').then(function(data) {
        console.log('pollen data', data)

        let width = 350
        let height = 250

        let x = d3.scaleLinear()
            .domain([0, 1000])
            .range([0, width])

        let y = d3.scaleBand()
            .range([0, height])
            .domain(data.map(d => d.factor))
            .padding(0.1)
        
        d3.select('#pollen').html('')

        let g = d3.select('#pollen').data([0]).append('g')
            .attr('width', width)
            .attr('height', height)
            .attr('transform', 'translate(120,0)')

        let pollenBarChart = g.selectAll('.bar').data(data)

        g.append("g")
            .style('font-size', '14px')
            .call(d3.axisLeft(y))
            .call(g => g.select(".domain").remove())
            
        pollenBarChart.enter()
            .append('rect')
            .classed('bar', true)
            .merge(pollenBarChart)
            .attr('x', x(0))
            .attr('y', d => y(d.factor))
            .attr('width', d => x(d.value))
            .attr('height', y.bandwidth())
            .attr('fill', d => d.fillColor)
        
    })
}

updateDateTime()
updateNewsData().then(updateNewsDisplay)
updateWeather()
updateMilkyWay()
updatePollen()

setInterval(updateDateTime, 1000);
setInterval(updateNewsData, 15 * 60 * 1000)
setInterval(updateWeather, 5 * 60 * 1000)
setInterval(updateNewsDisplay, 30 * 1000)
setInterval(updateMilkyWay, 15 * 60 * 1000)
setInterval(updatePollen, 15 * 60 * 1000)