import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:5000/api', // change if your backend port differs
  withCredentials: true // important for session cookies
})

export default instance
