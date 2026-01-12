//+------------------------------------------------------------------+
//|                                               Trade_Manager.mqh |
//|                        Order execution and management            |
//|                        Based on Ultimate System v19.0             |
//+------------------------------------------------------------------+
#property copyright   "{{AUTHOR_NAME}}"
#property version     "1.00"

#include <Trade/Trade.mqh>
#include <Trade/PositionInfo.mqh>
#include <Trade/SymbolInfo.mqh>

// ═══════════════════════════════════════════════════════════════════
// TRADE RESULT ENUM
// ═══════════════════════════════════════════════════════════════════

enum ENUM_TRADE_RESULT
{
   TRADE_SUCCESS = 0,
   TRADE_FAILED_INVALID_PRICE,
   TRADE_FAILED_INVALID_VOLUME,
   TRADE_FAILED_INVALID_SL,
   TRADE_FAILED_INVALID_TP,
   TRADE_FAILED_SPREAD_HIGH,
   TRADE_FAILED_MARGIN,
   TRADE_FAILED_MAX_POSITIONS,
   TRADE_FAILED_DUPLICATE,
   TRADE_FAILED_EXECUTION,
   TRADE_FAILED_DISABLED
};

// ═══════════════════════════════════════════════════════════════════
// TRADE REQUEST STRUCTURE
// ═══════════════════════════════════════════════════════════════════

struct TradeRequest
{
   string   symbol;
   int      direction;      // 1=BUY, -1=SELL
   double   volume;
   double   price;
   double   sl;
   double   tp;
   string   comment;
   ulong    magic;

   void Clear()
   {
      symbol = "";
      direction = 0;
      volume = 0;
      price = 0;
      sl = 0;
      tp = 0;
      comment = "";
      magic = 0;
   }
};

// ═══════════════════════════════════════════════════════════════════
// TRADE MANAGER CLASS
// ═══════════════════════════════════════════════════════════════════

class CTradeManager
{
private:
   CTrade         m_Trade;
   CPositionInfo  m_Position;
   CSymbolInfo    m_Symbol;

   ulong          m_Magic;
   int            m_MaxRetries;
   int            m_RetryDelay;
   double         m_MaxSpreadPoints;
   bool           m_TradingEnabled;

   string         m_LastError;
   ENUM_TRADE_RESULT m_LastResult;

public:
   CTradeManager()
   {
      m_Magic = 0;
      m_MaxRetries = 3;
      m_RetryDelay = 500;
      m_MaxSpreadPoints = 0;
      m_TradingEnabled = true;
      m_LastError = "";
      m_LastResult = TRADE_SUCCESS;
   }

   // ═══════════════════════════════════════════════════════════════
   // INITIALIZATION
   // ═══════════════════════════════════════════════════════════════

   bool Init(ulong magic, int deviation = 10)
   {
      m_Magic = magic;
      m_Trade.SetExpertMagicNumber(magic);
      m_Trade.SetDeviationInPoints(deviation);
      m_Trade.SetTypeFilling(ORDER_FILLING_IOC);
      m_Trade.SetAsyncMode(false);

      return true;
   }

   void SetMaxSpread(double points) { m_MaxSpreadPoints = points; }
   void SetMaxRetries(int retries) { m_MaxRetries = retries; }
   void SetRetryDelay(int ms) { m_RetryDelay = ms; }
   void EnableTrading(bool enable) { m_TradingEnabled = enable; }

   string GetLastError() { return m_LastError; }
   ENUM_TRADE_RESULT GetLastResult() { return m_LastResult; }

   // ═══════════════════════════════════════════════════════════════
   // TRADE EXECUTION
   // ═══════════════════════════════════════════════════════════════

   ENUM_TRADE_RESULT OpenTrade(TradeRequest &request)
   {
      m_LastError = "";
      m_LastResult = TRADE_SUCCESS;

      // Check if trading enabled
      if(!m_TradingEnabled)
      {
         m_LastError = "Trading disabled";
         m_LastResult = TRADE_FAILED_DISABLED;
         return m_LastResult;
      }

      // Initialize symbol
      if(!m_Symbol.Name(request.symbol))
      {
         m_LastError = "Invalid symbol: " + request.symbol;
         m_LastResult = TRADE_FAILED_EXECUTION;
         return m_LastResult;
      }
      m_Symbol.Refresh();
      m_Symbol.RefreshRates();

      // Check spread
      if(m_MaxSpreadPoints > 0)
      {
         double spread = m_Symbol.Spread();
         if(spread > m_MaxSpreadPoints)
         {
            m_LastError = StringFormat("Spread too high: %.1f > %.1f", spread, m_MaxSpreadPoints);
            m_LastResult = TRADE_FAILED_SPREAD_HIGH;
            return m_LastResult;
         }
      }

      // Validate volume
      if(!ValidateVolume(request.volume, request.symbol))
      {
         return m_LastResult;
      }

      // Set price if not provided
      if(request.price == 0)
      {
         request.price = (request.direction > 0) ? m_Symbol.Ask() : m_Symbol.Bid();
      }

      // Validate SL/TP
      if(!ValidateSLTP(request))
      {
         return m_LastResult;
      }

      // Execute with retry
      bool success = false;
      for(int i = 0; i < m_MaxRetries && !success; i++)
      {
         if(i > 0)
         {
            Sleep(m_RetryDelay);
            m_Symbol.RefreshRates();
            request.price = (request.direction > 0) ? m_Symbol.Ask() : m_Symbol.Bid();
         }

         if(request.direction > 0)
         {
            success = m_Trade.Buy(request.volume, request.symbol, request.price,
                                  request.sl, request.tp, request.comment);
         }
         else
         {
            success = m_Trade.Sell(request.volume, request.symbol, request.price,
                                   request.sl, request.tp, request.comment);
         }
      }

      if(!success)
      {
         m_LastError = StringFormat("Execution failed: %d - %s",
                                    m_Trade.ResultRetcode(),
                                    m_Trade.ResultRetcodeDescription());
         m_LastResult = TRADE_FAILED_EXECUTION;
      }

      return m_LastResult;
   }

   bool Buy(string symbol, double volume, double sl = 0, double tp = 0, string comment = "")
   {
      TradeRequest req;
      req.symbol = symbol;
      req.direction = 1;
      req.volume = volume;
      req.price = 0;
      req.sl = sl;
      req.tp = tp;
      req.comment = comment;
      req.magic = m_Magic;

      return (OpenTrade(req) == TRADE_SUCCESS);
   }

   bool Sell(string symbol, double volume, double sl = 0, double tp = 0, string comment = "")
   {
      TradeRequest req;
      req.symbol = symbol;
      req.direction = -1;
      req.volume = volume;
      req.price = 0;
      req.sl = sl;
      req.tp = tp;
      req.comment = comment;
      req.magic = m_Magic;

      return (OpenTrade(req) == TRADE_SUCCESS);
   }

   // ═══════════════════════════════════════════════════════════════
   // POSITION MANAGEMENT
   // ═══════════════════════════════════════════════════════════════

   bool ClosePosition(ulong ticket)
   {
      if(!m_Position.SelectByTicket(ticket))
      {
         m_LastError = "Position not found: " + IntegerToString(ticket);
         return false;
      }

      return m_Trade.PositionClose(ticket);
   }

   bool CloseAllPositions(string symbol = "")
   {
      bool allClosed = true;

      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(!m_Position.SelectByIndex(i)) continue;
         if(m_Position.Magic() != m_Magic) continue;
         if(symbol != "" && m_Position.Symbol() != symbol) continue;

         if(!m_Trade.PositionClose(m_Position.Ticket()))
         {
            allClosed = false;
         }
      }

      return allClosed;
   }

   bool ModifySL(ulong ticket, double newSL)
   {
      if(!m_Position.SelectByTicket(ticket))
      {
         return false;
      }

      return m_Trade.PositionModify(ticket, newSL, m_Position.TakeProfit());
   }

   bool ModifyTP(ulong ticket, double newTP)
   {
      if(!m_Position.SelectByTicket(ticket))
      {
         return false;
      }

      return m_Trade.PositionModify(ticket, m_Position.StopLoss(), newTP);
   }

   bool ModifySLTP(ulong ticket, double newSL, double newTP)
   {
      return m_Trade.PositionModify(ticket, newSL, newTP);
   }

   // ═══════════════════════════════════════════════════════════════
   // TRAILING STOP
   // ═══════════════════════════════════════════════════════════════

   bool ApplyTrailingStop(ulong ticket, double trailDistance, double activationDistance = 0)
   {
      if(!m_Position.SelectByTicket(ticket))
      {
         return false;
      }

      if(!m_Symbol.Name(m_Position.Symbol()))
      {
         return false;
      }
      m_Symbol.RefreshRates();

      double currentPrice = m_Position.PriceCurrent();
      double openPrice = m_Position.PriceOpen();
      double currentSL = m_Position.StopLoss();
      double point = m_Symbol.Point();
      int digits = m_Symbol.Digits();

      // Check activation
      if(activationDistance > 0)
      {
         double profitPoints = 0;
         if(m_Position.PositionType() == POSITION_TYPE_BUY)
         {
            profitPoints = (currentPrice - openPrice) / point;
         }
         else
         {
            profitPoints = (openPrice - currentPrice) / point;
         }

         if(profitPoints < activationDistance)
         {
            return false; // Not yet activated
         }
      }

      // Calculate new SL
      double newSL = 0;
      if(m_Position.PositionType() == POSITION_TYPE_BUY)
      {
         newSL = NormalizeDouble(currentPrice - trailDistance, digits);
         if(newSL > currentSL && newSL > openPrice)
         {
            return m_Trade.PositionModify(ticket, newSL, m_Position.TakeProfit());
         }
      }
      else // SELL
      {
         newSL = NormalizeDouble(currentPrice + trailDistance, digits);
         if((currentSL == 0 || newSL < currentSL) && newSL < openPrice)
         {
            return m_Trade.PositionModify(ticket, newSL, m_Position.TakeProfit());
         }
      }

      return false;
   }

   // ═══════════════════════════════════════════════════════════════
   // BREAK EVEN
   // ═══════════════════════════════════════════════════════════════

   bool ApplyBreakEven(ulong ticket, double triggerProfit, double lockInProfit = 0)
   {
      if(!m_Position.SelectByTicket(ticket))
      {
         return false;
      }

      double profit = m_Position.Profit();
      double currentSL = m_Position.StopLoss();
      double openPrice = m_Position.PriceOpen();
      double point = m_Symbol.Point();
      int digits = m_Symbol.Digits();

      if(profit < triggerProfit)
      {
         return false; // Not enough profit
      }

      double newSL = 0;
      if(m_Position.PositionType() == POSITION_TYPE_BUY)
      {
         newSL = NormalizeDouble(openPrice + lockInProfit * point, digits);
         if(currentSL < openPrice)
         {
            return m_Trade.PositionModify(ticket, newSL, m_Position.TakeProfit());
         }
      }
      else // SELL
      {
         newSL = NormalizeDouble(openPrice - lockInProfit * point, digits);
         if(currentSL > openPrice || currentSL == 0)
         {
            return m_Trade.PositionModify(ticket, newSL, m_Position.TakeProfit());
         }
      }

      return false;
   }

   // ═══════════════════════════════════════════════════════════════
   // POSITION QUERIES
   // ═══════════════════════════════════════════════════════════════

   int CountPositions(string symbol = "")
   {
      int count = 0;
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(m_Position.SelectByIndex(i))
         {
            if(m_Position.Magic() != m_Magic) continue;
            if(symbol != "" && m_Position.Symbol() != symbol) continue;
            count++;
         }
      }
      return count;
   }

   int CountBuyPositions(string symbol = "")
   {
      int count = 0;
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(m_Position.SelectByIndex(i))
         {
            if(m_Position.Magic() != m_Magic) continue;
            if(symbol != "" && m_Position.Symbol() != symbol) continue;
            if(m_Position.PositionType() == POSITION_TYPE_BUY)
               count++;
         }
      }
      return count;
   }

   int CountSellPositions(string symbol = "")
   {
      int count = 0;
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(m_Position.SelectByIndex(i))
         {
            if(m_Position.Magic() != m_Magic) continue;
            if(symbol != "" && m_Position.Symbol() != symbol) continue;
            if(m_Position.PositionType() == POSITION_TYPE_SELL)
               count++;
         }
      }
      return count;
   }

   double GetTotalProfit(string symbol = "")
   {
      double profit = 0;
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(m_Position.SelectByIndex(i))
         {
            if(m_Position.Magic() != m_Magic) continue;
            if(symbol != "" && m_Position.Symbol() != symbol) continue;
            profit += m_Position.Profit() + m_Position.Swap() + m_Position.Commission();
         }
      }
      return profit;
   }

   double GetTotalVolume(string symbol = "")
   {
      double volume = 0;
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(m_Position.SelectByIndex(i))
         {
            if(m_Position.Magic() != m_Magic) continue;
            if(symbol != "" && m_Position.Symbol() != symbol) continue;
            volume += m_Position.Volume();
         }
      }
      return volume;
   }

   bool HasPosition(string symbol)
   {
      return (CountPositions(symbol) > 0);
   }

private:
   // ═══════════════════════════════════════════════════════════════
   // VALIDATION
   // ═══════════════════════════════════════════════════════════════

   bool ValidateVolume(double volume, string symbol)
   {
      double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
      double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
      double stepLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);

      if(volume < minLot)
      {
         m_LastError = StringFormat("Volume too small: %.2f < %.2f", volume, minLot);
         m_LastResult = TRADE_FAILED_INVALID_VOLUME;
         return false;
      }

      if(volume > maxLot)
      {
         m_LastError = StringFormat("Volume too large: %.2f > %.2f", volume, maxLot);
         m_LastResult = TRADE_FAILED_INVALID_VOLUME;
         return false;
      }

      return true;
   }

   bool ValidateSLTP(TradeRequest &request)
   {
      double point = m_Symbol.Point();
      double stopsLevel = m_Symbol.StopsLevel() * point;

      if(request.sl != 0)
      {
         double slDistance = MathAbs(request.price - request.sl);
         if(slDistance < stopsLevel)
         {
            m_LastError = StringFormat("SL too close: %.5f < %.5f", slDistance, stopsLevel);
            m_LastResult = TRADE_FAILED_INVALID_SL;
            return false;
         }
      }

      if(request.tp != 0)
      {
         double tpDistance = MathAbs(request.price - request.tp);
         if(tpDistance < stopsLevel)
         {
            m_LastError = StringFormat("TP too close: %.5f < %.5f", tpDistance, stopsLevel);
            m_LastResult = TRADE_FAILED_INVALID_TP;
            return false;
         }
      }

      return true;
   }
};

//+------------------------------------------------------------------+
