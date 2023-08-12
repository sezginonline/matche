import Alamofire
import Combine

class TestViewModel: ObservableObject {
    @Published var result: String = ""
    
    func fetchData() {
        AF.request("http://192.168.1.188/api/v1/test/me").response { response in
            if let data = response.data {
                self.result = String(data: data, encoding: .utf8) ?? ""
            }
        }
    }
}
