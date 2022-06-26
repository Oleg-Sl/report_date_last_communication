
export default class Request {
    constructor(api) {
        this.api = api;
        // this.auth = new Auth(DOMAIN);
    }

    async init() {
        // инициализация объекта - авторизация и аутентификация
        await this.auth.init();
    }

    // присоединение параметров и выполнение GET запроса
    async GET(path, params={}) {
        
        // let token = await this.auth.getAccessToken();
        let options = {
            // headers: {Authorization: `Bearer ${token}`}
        };
        let url = this.api + path + "/";
        let urlGet = new URL(url);
        for (let key in params) {
            urlGet.searchParams.set(key, params[key]);
        }

        let response = await fetch(urlGet, options);
        if (response.ok) {
            let json = await response.json();
            return {
                error: false,
                result: json,
            };
        } else {
            let json = await response.json();
            alert("Ошибка: " + getStringDescErr(json));
            return {
                error: true,
                result: json,
            };
        }
    }
    
    // присоединение параметров и выполнение GET запроса - пагинация - извлечение всех данных 
    async GET_LONG(path, params={}) {
        let result = [];
        let url = this.api + path + "/";
        let urlGet = new URL(url);
        for (let key in params) {
            urlGet.searchParams.set(key, params[key]);
        }

        let i = 3
        while (i > 0) {
            i -= 1
            // let token = await this.auth.getAccessToken();
            let options = {
                // headers: {Authorization: `Bearer ${token}`}
            };
            let response = await fetch(urlGet, options);
            if (response.ok) {
                let json = await response.json();
                result = result.concat(json.results);
                urlGet = json.next;
                if (!urlGet) break;
            } else {
                let json = await response.json();
                alert("Ошибка: " + getStringDescErr(json));
                return {
                    error: true,
                    result: json,
                };
            }
        }
            
        return {
            error: false,
            result: result,
        };
    }

    async POST(path, data, params={}) {
        // let token = await this.auth.getAccessToken();
        let url = this.api + path + "/";
        let urlPost = new URL(url);
        for (let key in params) {
            urlGet.searchParams.set(key, params[key]);
        }
        let response = await fetch(urlPost, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                // 'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            let json = await response.json();
            return {
                error: false,
                result: json,
            };
        } else {
            let json = await response.json();
            // alert("Ошибка: " + getStringDescErr(json));
            console.log("Ошибка: " + getStringDescErr(json));
            return {
                error: true,
                result: json,
            };
        }
    }

    async PUT(path, data, params={}) {
        // let token = await this.auth.getAccessToken();
        let url = this.api + path + "/";
        let urlPost = new URL(url);
        for (let key in params) {
            urlGet.searchParams.set(key, params[key]);
        }
        let response = await fetch(urlPost, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                // 'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            let json = await response.json();
            return {
                error: false,
                result: json,
            };
        } else {
            let json = await response.json();
            alert("Ошибка: " + getStringDescErr(json));
            return {
                error: true,
                result: json,
            };
        }
    }

}


function getStringDescErr(err) {
    if (typeof(err) === "string") {
        return err;
    }
    if (typeof(err) === "number") {
        return String(err);
    }
    if (typeof(err) === "object" && Array.isArray(err)) {
        let errStr = "";
        for (let e of err) {
            errStr += String(e);
        }
        return errStr;
    }

    if (typeof(err) === "object" && !Array.isArray(err)) {
        let errStr = "";
        for (let key in err) {
            errStr += `${key} - ${err[key]}, `;
        }
        return errStr;
    }
}

