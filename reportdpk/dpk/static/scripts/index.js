import Request from './requests.js';
import BX from './bx24.js';
import TableStatistic from './table_statistic.js';

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

        // таблица - с статистикой по компаниям
        this.elementTableStatistic = document.querySelector('#tableStatisticData');
        this.loaderTableStatistic = document.querySelector('#loaderTableStatistic');
        this.tableStatistic = new TableStatistic(this.elementTableStatistic, loaderTableStatistic, this.bx24);
        
        this.selectedPageSize = document.querySelector('#selectedPageSize');
        this.selectedPageNumber = document.querySelector('#selectedPageNumber');
        this.elemMinDurationForCalcDpk = document.querySelector('#minDurationForCalcDpk');
        this.buttonGoToPage = document.querySelector('#buttonGoToPage');
        this.buttonGetStatistic = document.querySelector('#buttonGetStatistic');
    
        
        this.page = 1;
        this.order = "name";
    }

    async init() {
        
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
        
        this.userCurrent = await this.getCurrentUser();
        this.users = await this.getActiveUsers();
        
        this.tableStatistic.init(6 * 31, this.userCurrent, this.users);

        this.initHandler();
        await this.getStatistic();
    }

    initHandler() {
        buttonGoToPage.addEventListener('click', async (e) => {
            this.page = parseInt(this.selectedPageNumber.value);
            await this.getStatistic();
        });
        buttonGetStatistic.addEventListener('click', async (e) => {
            this.page = 1
            await this.getStatistic();
        });
        this.elementTableStatistic.addEventListener('click', async (e) => {
            if (e.target.tagName === "I" && $(".header-th-sort-data").has(e.target).length !== 0) {
                this.order = e.target.dataset.order;
                await this.getStatistic();
            } 
        })


    }

    // получить данные текущего пользователя
    async getCurrentUser() {
        let userCurrent = await this.bx24.callMethod('user.current', {});
        return userCurrent;
    }

    // получить данные список всех пользователей
    async getActiveUsers() {
        // "FILTER": {"ACTIVE": true}
        let usersList = await this.bx24.longBatchMethod('user.get', {});
        let userObj = {};
        for (let user of usersList) {
            let userId = user.ID;
            userObj[userId] = user;
        }
        return userObj;
    }
    // возвращает параметры запроса статистики
    getParamsRequest() {
        return {
            ordering: this.order,
            page: this.page,
            page_size: this.getPageSize(),
            duration: this.getMinDurationForCalcDpk(),
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

    async getStatistic() {

        this.tableStatistic.hideTable();

        let paramsRequest = this.getParamsRequest();
        console.log("paramsRequest = ", paramsRequest);

        this.companySummary = await this.requests.GET("statistic-company", paramsRequest);
        this.summaryByDirections = await this.requests.GET("statistic-direction", {
            direction: paramsRequest.direction
        });
        this.companySummaryByDirections = await this.requests.GET("statistic-company-direction", {
            companies: this.companySummary.result.results.map((obj) => obj.id_bx),
        });
        console.log("companySummary = ", this.companySummary);
        console.log("summaryByDirections = ", this.summaryByDirections);
        console.log("companySummaryByDirections = ", this.companySummaryByDirections);
        this.tableStatistic.renderTable(this.companySummary.result.results, this.summaryByDirections.result, this.companySummaryByDirections.result);
        this.tableStatistic.sortingSelection(this.order);

        this.tableStatistic.showTable();
    }

    getPageSize() {
        return this.selectedPageSize.value;
    }

    getMinDurationForCalcDpk() {
        return this.elemMinDurationForCalcDpk.value;
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


