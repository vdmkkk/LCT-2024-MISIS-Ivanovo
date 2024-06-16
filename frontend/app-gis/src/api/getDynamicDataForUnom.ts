import { ml } from 'src/boot/axios';

const getDynamicDataForUnom = async (unom: number) => {
  // const today = new Date().toISOString().split('.')[0];
  const today = '2024-04-01T00:00:00';
  const earlier = '2024-03-18T00:00:00';
  return await ml
    .post(
      `/predict_one?unom=${unom}&date=${today}&date_start=${earlier}&date_end=${today}&n=14`
    )
    .then((res) => {
      return res.data;
    })
    .catch((e) => {
      console.error(e);
    });
};

export default getDynamicDataForUnom;
