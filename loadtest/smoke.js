import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<300"],
  },
};

export default function () {
  const response = http.get(`${__ENV.BASE_URL}/books?q=dune`);
  check(response, { "status is 200": (r) => r.status === 200 });
  sleep(1);
}
