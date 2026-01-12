//+------------------------------------------------------------------+
//|                                              Trade_Manager.mqh   |
//|                                   Trade Execution Utility v1.0   |
//|                        Order execution, modification, closing    |
//+------------------------------------------------------------------+
#property copyright "Your Name"
#property link      "https://www.example.com"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>
#include <Trade\SymbolInfo.mqh>

//+------------------------------------------------------------------+
//| Trade Request Structure                                           |
//+------------------------------------------------------------------+
struct TradeRequest
{
   string   symbol;
   int      direction;        // 1 = Buy, -1 = Sell
   double   lotSize;
   double   stopLoss;
   double   takeProfit;
   string   comment;
   ulong    magic;
   int      slippage;
   
   void Clear()
   {
      symbol = "";
      direction = 0;
      lotSize = 0;
      stopLoss = 0;
      takeProfit = 0;
      comment = "";
      magic = 0;
      slippage = 30;
   }
};

//+------------------------------------------------------------------+
//| Trade Result Structure                                            |
//+------------------------------------------------------------------+
struct TradeResult
{
   bool     success;
   ulong    ticket;
   double   openPrice;
   double   volume;
   uint     retcode;
   string   retcodeDesc;
   
   void SetSuccess(ulong tkt, double price, double vol)
   {
      success = true;
      ticket = tkt;
      openPrice = price;
      volume = vol;
      retcode = 0;
      retcodeDesc = "";
   }
   
   void SetFailure(uint code, string desc)
   {
      success = false;
      ticket = 0;
      openPrice = 0;
      volume = 0;
      retcode = code;
      retcodeDesc = desc;
   }
};

//+------------------------------------------------------------------+
//| Trade Statistics Structure                                        |
//+------------------------------------------------------------------+
struct TradeStatistics
{
   int      totalTrades;
   int      winningTrades;
   int      losingTrades;
   double   totalProfit;
   double   totalLoss;
   double   largestWin;
   double   largestLoss;
   double   averageWin;
   double   averageLoss;
   
   double GetWinRate()
   {
      if(totalTrades == 0) return 0;
      return (double)winningTrades / totalTrades * 100;
   }
   
   double GetProfitFactor()
   {
      if(totalLoss == 0) return 0;
      return MathAbs(totalProfit / totalLoss);
   }
   
   double GetExpectancy()
   {
      if(totalTrades == 0) return 0;
      return (totalProfit + totalLoss) / totalTrades;
   }
   
   void Reset()
   {
      totalTrades = 0;
      winningTrades = 0;
      losingTrades = 0;
      totalProfit = 0;
      totalLoss = 0;
      largestWin = 0;
      largestLoss = 0;
      averageWin = 0;
      averageLoss = 0;
   }
};

//+------------------------------------------------------------------+
//| Trade Manager Class                                               |
//+------------------------------------------------------------------+
class CTradeManager
{
private:
   CTrade         m_Trade;
   CPositionInfo  m_Position;
   COrderInfo     m_Order;
   CSymbolInfo    m_Symbol;
   
   ulong          m_Magic;
   string         m_Comment;
   int            m_Slippage;
   
   TradeStatistics m_Stats;
   
   //--- Cooldown
   datetime       m_LastTradeTime;
   int            m_CooldownMinutes;
   
public:
   //--- Constructor
   CTradeManager()
   {
      m_Magic = 0;
      m_Comment = "";
      m_Slippage = 30;
      m_LastTradeTime = 0;
      m_CooldownMinutes = 0;
      m_Stats.Reset();
   }
   
   //--- Initialize
   bool Init(string symbol, ulong magic, string comment = "")
   {
      if(!m_Symbol.Name(symbol))
         return false;
      
      m_Magic = magic;
      m_Comment = comment;
      
      m_Trade.SetExpertMagicNumber(magic);
      m_Trade.SetDeviationInPoints(m_Slippage);
      m_Trade.SetTypeFilling(ORDER_FILLING_IOC);
      m_Trade.SetAsyncMode(false);
      
      return true;
   }
   
   //--- Settings
   void SetSlippage(int slippage)  { m_Slippage = slippage; m_Trade.SetDeviationInPoints(slippage); }
   void SetCooldown(int minutes)   { m_CooldownMinutes = minutes; }
   void SetComment(string comment) { m_Comment = comment; }
   
   //+------------------------------------------------------------------+
   //| Trade Execution                                                   |
   //+------------------------------------------------------------------+
   
   //--- Execute trade from request
   TradeResult ExecuteTrade(TradeRequest &request)
   {
      TradeResult result;
      
      //--- Validate request
      if(request.lotSize <= 0 || request.direction == 0)
      {
         result.SetFailure(10015, "Invalid trade request");
         return result;
      }
      
      //--- Check cooldown
      if(!CheckCooldown())
      {
         result.SetFailure(10016, "Cooldown active");
         return result;
      }
      
      //--- Refresh symbol
      m_Symbol.Name(request.symbol);
      m_Symbol.Refresh();
      m_Symbol.RefreshRates();
      
      //--- Get price
      double price = (request.direction > 0) ? m_Symbol.Ask() : m_Symbol.Bid();
      
      //--- Execute
      bool success = false;
      
      if(request.direction > 0)
      {
         success = m_Trade.Buy(request.lotSize, request.symbol, price,
                               request.stopLoss, request.takeProfit, request.comment);
      }
      else
      {
         success = m_Trade.Sell(request.lotSize, request.symbol, price,
                                request.stopLoss, request.takeProfit, request.comment);
      }
      
      //--- Process result
      if(success && m_Trade.ResultRetcode() == TRADE_RETCODE_DONE)
      {
         result.SetSuccess(m_Trade.ResultOrder(), m_Trade.ResultPrice(), m_Trade.ResultVolume());
         m_LastTradeTime = TimeCurrent();
      }
      else
      {
         result.SetFailure(m_Trade.ResultRetcode(), m_Trade.ResultRetcodeDescription());
      }
      
      return result;
   }
   
   //--- Simple buy
   TradeResult Buy(double lots, double sl = 0, double tp = 0, string comment = "")
   {
      TradeRequest req;
      req.symbol = m_Symbol.Name();
      req.direction = 1;
      req.lotSize = lots;
      req.stopLoss = sl;
      req.takeProfit = tp;
      req.comment = (comment == "") ? m_Comment : comment;
      req.magic = m_Magic;
      req.slippage = m_Slippage;
      
      return ExecuteTrade(req);
   }
   
   //--- Simple sell
   TradeResult Sell(double lots, double sl = 0, double tp = 0, string comment = "")
   {
      TradeRequest req;
      req.symbol = m_Symbol.Name();
      req.direction = -1;
      req.lotSize = lots;
      req.stopLoss = sl;
      req.takeProfit = tp;
      req.comment = (comment == "") ? m_Comment : comment;
      req.magic = m_Magic;
      req.slippage = m_Slippage;
      
      return ExecuteTrade(req);
   }
   
   //+------------------------------------------------------------------+
   //| Position Management                                               |
   //+------------------------------------------------------------------+
   
   //--- Close position by ticket
   bool ClosePosition(ulong ticket)
   {
      if(!m_Position.SelectByTicket(ticket))
         return false;
      
      return m_Trade.PositionClose(ticket);
   }
   
   //--- Close all positions for symbol
   int CloseAllPositions(string symbol = "")
   {
      int closed = 0;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(!m_Position.SelectByIndex(i))
            continue;
         
         if(m_Position.Magic() != m_Magic)
            continue;
         
         if(symbol != "" && m_Position.Symbol() != symbol)
            continue;
         
         if(m_Trade.PositionClose(m_Position.Ticket()))
            closed++;
      }
      
      return closed;
   }
   
   //--- Modify position SL/TP
   bool ModifyPosition(ulong ticket, double sl, double tp)
   {
      if(!m_Position.SelectByTicket(ticket))
         return false;
      
      return m_Trade.PositionModify(ticket, sl, tp);
   }
   
   //--- Move stop to breakeven
   bool MoveToBreakeven(ulong ticket, double minProfit = 0)
   {
      if(!m_Position.SelectByTicket(ticket))
         return false;
      
      m_Symbol.Name(m_Position.Symbol());
      m_Symbol.Refresh();
      
      double openPrice = m_Position.PriceOpen();
      double currentPrice = (m_Position.PositionType() == POSITION_TYPE_BUY) ? 
                            m_Symbol.Bid() : m_Symbol.Ask();
      double currentSL = m_Position.StopLoss();
      
      //--- Calculate profit in points
      double profitPoints;
      if(m_Position.PositionType() == POSITION_TYPE_BUY)
         profitPoints = (currentPrice - openPrice) / m_Symbol.Point();
      else
         profitPoints = (openPrice - currentPrice) / m_Symbol.Point();
      
      //--- Check if enough profit
      if(profitPoints < minProfit)
         return false;
      
      //--- Check if SL already at breakeven
      if(m_Position.PositionType() == POSITION_TYPE_BUY)
      {
         if(currentSL >= openPrice)
            return true;  // Already at or past breakeven
      }
      else
      {
         if(currentSL <= openPrice && currentSL > 0)
            return true;
      }
      
      return m_Trade.PositionModify(ticket, openPrice, m_Position.TakeProfit());
   }
   
   //--- Trail stop loss
   bool TrailStop(ulong ticket, double trailPoints)
   {
      if(!m_Position.SelectByTicket(ticket))
         return false;
      
      m_Symbol.Name(m_Position.Symbol());
      m_Symbol.Refresh();
      
      double point = m_Symbol.Point();
      double currentSL = m_Position.StopLoss();
      double newSL;
      
      if(m_Position.PositionType() == POSITION_TYPE_BUY)
      {
         newSL = m_Symbol.Bid() - trailPoints * point;
         if(newSL <= currentSL)
            return false;  // Don't move SL down
      }
      else
      {
         newSL = m_Symbol.Ask() + trailPoints * point;
         if(currentSL > 0 && newSL >= currentSL)
            return false;  // Don't move SL up
      }
      
      newSL = NormalizeDouble(newSL, m_Symbol.Digits());
      
      return m_Trade.PositionModify(ticket, newSL, m_Position.TakeProfit());
   }
   
   //--- Partial close
   bool PartialClose(ulong ticket, double percent)
   {
      if(!m_Position.SelectByTicket(ticket))
         return false;
      
      double volume = m_Position.Volume();
      double closeVolume = volume * percent / 100.0;
      
      //--- Normalize volume
      m_Symbol.Name(m_Position.Symbol());
      m_Symbol.Refresh();
      
      double lotStep = m_Symbol.LotsStep();
      closeVolume = MathFloor(closeVolume / lotStep) * lotStep;
      
      if(closeVolume < m_Symbol.LotsMin())
         return false;
      
      return m_Trade.PositionClosePartial(ticket, closeVolume);
   }
   
   //+------------------------------------------------------------------+
   //| Position Info                                                     |
   //+------------------------------------------------------------------+
   
   //--- Count positions
   int CountPositions(string symbol = "")
   {
      int count = 0;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(!m_Position.SelectByIndex(i))
            continue;
         
         if(m_Position.Magic() != m_Magic)
            continue;
         
         if(symbol != "" && m_Position.Symbol() != symbol)
            continue;
         
         count++;
      }
      
      return count;
   }
   
   //--- Get total profit/loss
   double GetTotalProfit(string symbol = "")
   {
      double total = 0;
      
      for(int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if(!m_Position.SelectByIndex(i))
            continue;
         
         if(m_Position.Magic() != m_Magic)
            continue;
         
         if(symbol != "" && m_Position.Symbol() != symbol)
            continue;
         
         total += m_Position.Profit() + m_Position.Swap() + m_Position.Commission();
      }
      
      return total;
   }
   
   //--- Check if position exists
   bool HasPosition(string symbol = "")
   {
      return CountPositions(symbol) > 0;
   }
   
   //+------------------------------------------------------------------+
   //| Statistics                                                        |
   //+------------------------------------------------------------------+
   
   //--- Record closed trade
   void RecordTrade(double profit)
   {
      m_Stats.totalTrades++;
      
      if(profit > 0)
      {
         m_Stats.winningTrades++;
         m_Stats.totalProfit += profit;
         if(profit > m_Stats.largestWin)
            m_Stats.largestWin = profit;
      }
      else if(profit < 0)
      {
         m_Stats.losingTrades++;
         m_Stats.totalLoss += profit;
         if(profit < m_Stats.largestLoss)
            m_Stats.largestLoss = profit;
      }
      
      //--- Update averages
      if(m_Stats.winningTrades > 0)
         m_Stats.averageWin = m_Stats.totalProfit / m_Stats.winningTrades;
      if(m_Stats.losingTrades > 0)
         m_Stats.averageLoss = m_Stats.totalLoss / m_Stats.losingTrades;
   }
   
   //--- Get statistics
   TradeStatistics GetStatistics() { return m_Stats; }
   void ResetStatistics() { m_Stats.Reset(); }
   
   //+------------------------------------------------------------------+
   //| Utilities                                                         |
   //+------------------------------------------------------------------+
   
   //--- Check cooldown
   bool CheckCooldown()
   {
      if(m_CooldownMinutes <= 0)
         return true;
      
      if(m_LastTradeTime == 0)
         return true;
      
      datetime cooldownEnd = m_LastTradeTime + m_CooldownMinutes * 60;
      return TimeCurrent() >= cooldownEnd;
   }
   
   //--- Get seconds until cooldown ends
   int GetCooldownRemaining()
   {
      if(m_CooldownMinutes <= 0 || m_LastTradeTime == 0)
         return 0;
      
      datetime cooldownEnd = m_LastTradeTime + m_CooldownMinutes * 60;
      int remaining = (int)(cooldownEnd - TimeCurrent());
      
      return (remaining > 0) ? remaining : 0;
   }
   
   //--- Get last trade time
   datetime GetLastTradeTime() { return m_LastTradeTime; }
   
   //--- Get trade object reference
   CTrade* GetTrade() { return &m_Trade; }
};

//+------------------------------------------------------------------+
