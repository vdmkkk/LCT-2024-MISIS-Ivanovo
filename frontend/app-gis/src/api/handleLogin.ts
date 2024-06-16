import { api } from 'src/boot/axios';
import Cookies from 'js-cookie';

const login = async (login: string, password: string) => {
  return await api
    .post(`/login?login=${login}&password=${password}`)
    .then((res) => {
      Cookies.set('_token', res.data['JWT'], { expires: 9999 });
    })
    .catch((e) => {
      console.error(e);
    });
};

export default login;
