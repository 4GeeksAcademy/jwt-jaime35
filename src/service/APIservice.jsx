// Get the backend URL from environment variables
const backendUrl = import.meta.env.VITE_BACKEND_URL;

// Check if the backend URL is defined
if (!backendUrl) {
    throw new Error("VITE_BACKEND_URL is not defined in .env file");
}

// Hello route (test)
export const loadMessage = async (dispatch) => {
    try {
        const response = await fetch(`${backendUrl}/hello`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        const data = await response.json();

        if (response.ok) {
            dispatch({ type: "set_hello", payload: data.message });
        }

        return data;

    } catch (error) {
        throw new Error("Could not fetch the message from the backend. Please check if the backend is running and the backend port is public.");
    }
};

// SIGNUP
export const createSignup = async (dispatch, info) => {
    try {
        const response = await fetch(`${backendUrl}/api/signup`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(info)
        });

        if (response.status === 201) {
            const data = await response.json();
            dispatch({ type: "signup", payload: data.user });
            return { success: true, message: "Signup successful! Please login." };
        } else {
            const errorData = await response.json();
            return {
                success: false,
                message: errorData.error || errorData.msg || "Signup failed."
            };
        }

    } catch (error) {
        console.error("Signup error:", error);
        return { success: false, message: "Network error. Please try again later." };
    }
};

// LOGIN
export const createLogin = async (dispatch, info) => {
    try {
        const response = await fetch(`${backendUrl}/api/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(info)
        });

        if (response.ok) {
            const data = await response.json();
            sessionStorage.setItem("authToken", JSON.stringify(data));

            dispatch({ type: "login", payload: data });

            dispatch({
                type: "profile",
                payload: {
                    id: data.user_id,
                    email: data.email,
                }
            });

            return { success: true };
        } else {
            const errorMsg = await response.json();
            return {
                success: false,
                message: errorMsg.error || errorMsg.msg || "Login failed."
            };
        }

    } catch (error) {
        console.error("Login error:", error);
        return { success: false, message: "Network error. Please try again later." };
    }
};

// GET PROFILE
export const createProfile = async (dispatch) => {
    const storedData = sessionStorage.getItem("authToken");

    let token = null;
    if (storedData) {
        try {
            token = JSON.parse(storedData).token;
        } catch {
            return { success: false, message: "Invalid token format." };
        }
    }

    if (!token) {
        return { success: false, message: "No authentication token found." };
    }

    try {
        const response = await fetch(`${backendUrl}/api/profile`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 200) {
            const data = await response.json();
            dispatch({ type: "profile", payload: data.user });
            return { success: true };
        } else {
            const errorMsg = await response.json();
            return {
                success: false,
                message: errorMsg.error || errorMsg.msg || "Profile fetch failed."
            };
        }

    } catch (error) {
        console.error("Profile fetch error:", error);
        return { success: false, message: "Network error. Please try again later." };
    }
};

// LOGOUT
export const logoutUser = async (dispatch) => {
    const storedData = sessionStorage.getItem("authToken");

    if (!storedData) {
        return { success: false, message: "No token found in session." };
    }

    let token = null;
    try {
        token = JSON.parse(storedData).token;
    } catch {
        return { success: false, message: "Invalid token format." };
    }

    try {
        const response = await fetch(`${backendUrl}/api/logout`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            sessionStorage.removeItem("authToken");
            dispatch({ type: "login", payload: [] });
            dispatch({ type: "profile", payload: null });
            return { success: true, message: "Logged out successfully." };
        } else {
            return { success: false, message: "Logout unsuccessful." };
        }

    } catch (error) {
        console.error("Logout error:", error);
        return { success: false, message: "Network error during logout." };
    }
};