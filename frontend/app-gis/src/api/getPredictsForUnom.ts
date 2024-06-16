import { ml } from 'src/boot/axios';

const getPredictsByUnom = async (unom: number) => {
  // const today = new Date().toISOString().split('.')[0];
  const today = process.env.VUE_APP_START_DATE;
  return await ml
    .post(
      `/predict_one?unom=${unom}&date=${today}&date_start=${today}&date_end=${today}&n=14`
    )
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getPredictsByUnom;
