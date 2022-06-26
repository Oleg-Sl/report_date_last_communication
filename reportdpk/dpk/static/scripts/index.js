import Request from './requests.js';
import BX from './bx24.js';

import {FilterCompany,} from './filters/filter.js';
import WindowSearchUser from './filters/user.js';
import FilterDirection from './filters/direction.js';
import {FilterSingle, } from './filters/single.js';
import {FilterRange, } from './filters/range.js';


class App {
    constructor(requests, bx24) {
        this.requests = requests;
        this.bx24 = bx24;
        
        // фильтр - КОМПАНИИ
        this.elementFilterCompany = document.querySelector('#filterCompany');
        this.filterCompany = new FilterCompany(this.elementFilterCompany, this.requests, 'companies');
        // фильтр - ОТВЕТСТВЕННЫЙ
        this.elementFilterResponsible = document.querySelector('#filterResponsible');
        this.filterResponsible = new WindowSearchUser(this.elementFilterResponsible, bx24);
        // фильтр - НАПРАВЛЕНИЯ СДЕЛОК
        this.elementFilterDirection = document.querySelector('#filterDirection');
        this.filterDirection = new FilterDirection(this.elementFilterDirection, this.requests, 'directions');
        // фильтр - ОТРАСЛЬ
        this.elementFilterSector = document.querySelector('#filterSector');
        this.filterSector = new FilterSingle(this.elementFilterSector, this.requests, 'sector_companies', 'sector');
        // фильтр - РЕГИОН
        this.elementFilterRegion = document.querySelector('#filterRegion');
        this.filterRegion = new FilterSingle(this.elementFilterRegion, this.requests, 'region_companies', 'region');
        // фильтр - ИСТОЧНИК
        this.elementFilterSource = document.querySelector('#filterSource');
        this.filterSource = new FilterSingle(this.elementFilterSource, this.requests, 'source_companies', 'source');
        // фильтр - РЕКВИЗИТ-РЕГИОН
        this.elementRequisiteRegion = document.querySelector('#filterRequisiteRegion');
        this.filterRequisiteRegion = new FilterSingle(this.elementRequisiteRegion, this.requests, 'requisite_region', 'requisite_region');
        // фильтр - РЕКВИЗИТ-ГОРОД
        this.elementFilterRequisiteCity = document.querySelector('#filterRequisiteCity');
        this.filterRequisiteCity = new FilterSingle(this.elementFilterRequisiteCity, this.requests, 'requisites_city', 'requisites_city');
        // фильтр - ГОДОВОЙ ОБОРОТ КОМПАНИИ
        this.elementFilterRevenue = document.querySelector('#filterRevenue');
        this.filterRevenue = new FilterRange(this.elementFilterRevenue);
        // фильтр - КОЛИЧЕСТВО СОТРУДНИКОВ
        this.elementFilterEmployees = document.querySelector('#filterEmployees');
        this.filterEmployees = new FilterRange(this.elementFilterEmployees);

        // 
        
        this.selectedPageNumber = document.querySelector('#selectedPageNumber');
        this.buttonGoToPage = document.querySelector('#buttonGoToPage');
        this.buttonGetStatistic = document.querySelector('#buttonGetStatistic');
    
    }

    init() {
        this.filterCompany.init();
        this.filterResponsible.init();
        this.filterDirection.init();
        this.filterSector.init();
        this.filterRegion.init();
        this.filterSource.init();
        this.filterRequisiteRegion.init();
        this.filterRequisiteCity.init();
        this.filterRevenue.init();
        this.filterEmployees.init();
        
        this.initHandler();
    }

    initHandler() {
        buttonGoToPage.addEventListener('click', async (e) => {
            let page = parseInt(this.selectedPageNumber.value);
            await this.getStatistic(page);
        })
        buttonGetStatistic.addEventListener('click', async (e) => {
            let page = 1
            await this.getStatistic(page);
        })
    }

    getParamsRequest() {
        return {
            duration: 15,
            company: this.filterCompany.getRequestParameters().join(","),
            responsible: this.filterResponsible.getRequestParameters().join(","),
            direction: this.filterDirection.getRequestParameters().join(","),
            sector: this.filterSector.getRequestParameters(),
            region: this.filterRegion.getRequestParameters(),
            source: this.filterSource.getRequestParameters(),
            requisite_region: this.filterRequisiteRegion.getRequestParameters(),
            requisites_city: this.filterRequisiteCity.getRequestParameters(),
            revenue_min: this.filterRevenue.getMinValue(),
            revenue_max: this.filterRevenue.getMaxValue(),
            number_employees_min: this.filterEmployees.getMinValue(),
            number_employees_max: this.filterEmployees.getMaxValue(),
        }
    }

    async getStatistic(page) {
        let paramsRequest = this.getParamsRequest();

        console.log("paramsRequest = ", paramsRequest);
        this.companySummary = await this.requests.GET("statistic-company", paramsRequest);
        this.summaryByDirections = await this.requests.GET("statistic-direction", paramsRequest);
        
        this.companySummaryByDirections = await this.requests.GET("statistic-company-direction", {
            companies: this.companySummary.result.results.map((obj) => obj.id_bx),
            // directions: paramsRequest.direction
        });
        console.log("companySummary = ", this.companySummary);
        console.log("summaryByDirections = ", this.summaryByDirections);
        console.log("companySummaryByDirections = ", this.companySummaryByDirections);
        
    }
}


$(document).ready(function() {
    BX24.init(function(){
        console.log("Ready!!!");
        // const api = "http://127.0.0.1:8000/dpk/api/v1/";
        const api = "https://otchet.atonlab.ru/dpk/api/v1/";
        
        let bx24 = new BX();
        let requests = new Request(api);
        let app = new App(requests, bx24);
        app.init();
    })
});


