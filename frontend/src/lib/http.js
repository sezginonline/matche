const BASE_URL = 'https://match-e.com/api/v1/';

async function fetchWithAuth(url, options = {}) {
    
    const response = await fetch(`${BASE_URL}${url}`, {
        credentials: 'include',
        ...options,
        headers: {
            // In file uploads Content-Type is not application/json, instead multipart/form-data; boundary=..
            // 'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Language': localStorage.getItem("language") ?? "en",
            ...options.headers,
        },
    });

    // If the response is unauthorized, try to refresh the token
    if (response.status === 401) {
        const refreshResponse = await fetch(`${BASE_URL}auth/refresh`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                // 'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        if (refreshResponse.ok) {
            // If the token is successfully refreshed, try the original request again
            return await fetch(`${BASE_URL}${url}`, {
                credentials: 'include',
                ...options,
                headers: {
                    // 'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    ...options.headers,
                },
            });
        } else {
            window.location.href = '/' + (localStorage.getItem("language") ?? "en") + '/';
        }
    }

    return response;
}

const httpMethods = ['get', 'post', 'put', 'delete', 'patch'];

const http = {};

httpMethods.forEach((method) => {
    http[method] = async function (url, data, options = {}) {
        const fetchOptions = {
            method,
            ...options,
        };

        if (data) {
            fetchOptions.body = typeof data.get === 'function' && data.get("file") ? data : JSON.stringify(data);
        }

        const response = await fetchWithAuth(url, fetchOptions);
        if (response.ok) {
            return response.json();
        } else {
            const errorData = await response.json();
            throw errorData;
        }
    };
});

export { http };
