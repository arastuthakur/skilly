# Evaluates tiered pricing for billing accounts
class PriceCalculator
  # Calculates net discount for customer tier
  def calculate_discount(tier, amount)
    amount * 0.15
  end
end
