let DOMAIN = "https://otchet.atonlab.ru/";
let URL__CREATE_UPDATE_COMPANY = `${DOMAIN}/create-update-company/`;
let URL__CREATE_UPDATE_DEAL = `${DOMAIN}/create-update-deal/`;
let URL__CREATE_UPDATE_CALLS = `${DOMAIN}/create-update-calls/`;


async function callMethod(method, params = {}) {
    return new Promise((resolve, reject) => {
        let callback = result => {
            if (result.status != 200 || result.error()) {
                console.log(`${result.error()} (callMethod ${method}: ${JSON.stringify(params)})`);
                return reject("");
            }
            return resolve(result.data());
        };
        BX24.callMethod(method, params, callback);
    });
}


BX24.init(async function(){
    await callMethod(
        'event.bind',
        {
			"event": "ONCRMCOMPANYADD",
			"handler": URL__CREATE_UPDATE_COMPANY,
		},
		console.log('Обработчик ONCRMCOMPANYADD установлен')
    )
    await callMethod(
        'event.bind',
        {
			"event": "ONCRMCOMPANYUPDATE",
			"handler": URL__CREATE_UPDATE_COMPANY,
		},
		console.log('Обработчик ONCRMCOMPANYUPDATE установлен')
    )
    await callMethod(
        'event.bind',
        {
			"event": "ONCRMCOMPANYDELETE",
			"handler": URL__CREATE_UPDATE_COMPANY,
		},
		console.log('Обработчик ONCRMCOMPANYDELETE установлен')
    )
    await callMethod(
        'event.bind',
        {
			"event": "ONCRMDEALADD",
			"handler": URL__CREATE_UPDATE_DEAL,
		},
		console.log('Обработчик ONCRMDEALADD установлен')
    )
    await callMethod(
        'event.bind',
        {
			"event": "ONCRMDEALUPDATE",
			"handler": URL__CREATE_UPDATE_DEAL,
		},
		console.log('Обработчик ONCRMDEALUPDATE установлен')
    )
    await callMethod(
        'event.bind',
        {
			"event": "ONCRMDEALDELETE",
			"handler": URL__CREATE_UPDATE_DEAL,
		},
		console.log('Обработчик ONCRMDEALDELETE установлен')
    )
    await callMethod(
        'event.bind',
        {
			"event": "ONVOXIMPLANTCALLEND",
			"handler": URL__CREATE_UPDATE_CALLS,
		},
		console.log('Обработчик ONVOXIMPLANTCALLEND установлен')
    )

    BX24.installFinish();
});

