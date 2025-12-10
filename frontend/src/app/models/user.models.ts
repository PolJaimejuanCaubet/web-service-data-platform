export interface UserBase {
    full_name: string;
    username: string;
    email: string;
    role: string;
}


export interface UserCreate {
    full_name: string;
    username: string;
    email: string;
    password: string;

}

export interface UserLogin {
    username: string;
    password: string;
}

export interface UserUpdate {
    full_name: string;
    email: string;
}

export interface UserResponse extends UserBase {
    id?: string;     // _id de MongoDB convertido a string
    _id?: string;    // _id original de MongoDB
}

export interface RegisterResponse {
    message: string;
    user_id: string;
    email: string;
    role: string;
}


export interface LoginResponse {
    message: string;
    access_token: string;
    token_type: string;
    user: {
        id: string;
        username: string;
    };
}

export interface FastAPIError {
    detail: string;
}