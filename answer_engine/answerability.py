class AnswerabilityEstimator:
    def __init__(self):
        pass
        
    def is_in_domain(self, query: str, contexts: list[str]) -> bool:
        """
        Kiểm tra xem câu hỏi có nằm trong domain hay không dựa vào contexts trả về.
        Tạm thời sử dụng logic rule-based: Nếu không có context liên quan, suy ra Out-of-Domain.
        """
        if not contexts or len(contexts) == 0:
            return False
            
        # Nếu muốn nâng cao, có thể gọi một Model nhẹ để đánh giá Query vs Context tại đây
        return True
