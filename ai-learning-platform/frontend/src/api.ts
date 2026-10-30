import axios from 'axios';
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1'});
api.interceptors.request.use(config=>{const token=localStorage.getItem('token');if(token)config.headers.Authorization=`Bearer ${token}`;return config;});
export type Skill={id:number;name:string;category:string}; export type Role={id:number;name:string;description:string};
export function errorMessage(e:unknown){return axios.isAxiosError(e)?String(e.response?.data?.detail||e.message):'Unexpected error';}
