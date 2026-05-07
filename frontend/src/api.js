import axios from 'axios';

// Connect directly to the Ubuntu server's FastAPI
const API_URL = 'http://172.16.206.50:8000/api';

export const getBlockedIps = async () => {
  const response = await axios.get(`${API_URL}/firewall/blocked`);
  return response.data;
};

export const blockIp = async (ip_address, reason) => {
  const response = await axios.post(`${API_URL}/firewall/block`, {
    ip_address,
    reason
  });
  return response.data;
};

export const unblockIp = async (ip_address) => {
  const response = await axios.post(`${API_URL}/firewall/unblock`, {
    ip_address,
    reason: "Unblocked via SOC UI"
  });
  return response.data;
};
