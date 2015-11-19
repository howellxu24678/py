#if defined(WIN32) || defined(WIN64) || defined(OS_IS_WINDOWS)
//#include <SDKDDKVer.h>
//#include <stdio.h>
//#include <tchar.h>
#include <Windows.h>

#if defined(TESTDLL_EXPORTS)
#define MACLIAPI __declspec(dllexport)
#else
#define MACLIAPI __declspec(dllimport)
#endif
#define MACLI_STDCALL __stdcall
#define MACLI_EXPORTS __declspec(dllexport)
#else
#define MACLIAPI
#define MACLI_STDCALL
#define MACLI_EXPORTS
#if !defined __int64
#define __int64 long long
#endif
#endif

#include <string>


struct Server 
{
	char szIp[50];
	int	 nPort;
};

class NewLoginInfo
{
public:
	NewLoginInfo() 
	{
		int j = 0;
		memset(this, 0, sizeof(*this));
	}

public:

	char	account[50];			//账号
	char	accountName[50];		//账号名称 SendMsg的时候用
	char	password[50];
	int		accountType;			//账号类型
	int		autoReconnect;			//是否自动重连
	int		serverCount;			//服务器数量
	Server	servers[10];			//服务器
};

typedef void (* Fun_OnMsgPtr)(const char *msg, int len, const char *account, void *param);


Fun_OnMsgPtr  gCallBackFunPtr = NULL;
void* gCallBackParam = NULL;

typedef int (MACLI_STDCALL *Fun_Init) 
	(void*            parentHwnd, 
	int				 notifyMsg, 
	Fun_OnMsgPtr     funPtr, 
	void             *callBackParam);
typedef int (MACLI_STDCALL *Fun_NewMultiLogin)(NewLoginInfo *infos);
typedef int (MACLI_STDCALL *Fun_SendMsg)(
	const char *account, 
	const void *msg, 
	int len);
typedef int (MACLI_STDCALL *Fun_GetAccountState)(const char *account);
typedef int (MACLI_STDCALL *Fun_GetAccountCount)();
typedef int (MACLI_STDCALL *Fun_GetAccountByIndex)(
	int index, 
	char *account, 
	int *type);
typedef int (MACLI_STDCALL *Fun_Close)(const char *account);
typedef void (MACLI_STDCALL *Fun_Release)();


HMODULE					m_module;
Fun_Init				m_fInit;
Fun_NewMultiLogin		m_fNewMultiLogin;
Fun_SendMsg				m_fSendMsg;
Fun_GetAccountState		m_fGetAccountState;
Fun_GetAccountCount		m_fGetAccountCount;
Fun_GetAccountByIndex	m_fGetAccountByIndex;
Fun_Close				m_fClose;
Fun_Release				m_fRelease;



#ifdef __cplusplus

extern "C"
{
#endif
MACLIAPI int MACLI_STDCALL AxE_Init(void*             parentHwnd, 
		int            notifyMsg, 
		Fun_OnMsgPtr    funPtr, 
		void            *callBackParam);

MACLIAPI int MACLI_STDCALL AxE_NewMultiLogin(NewLoginInfo *infos);

MACLIAPI int MACLI_STDCALL AxE_SendMsg(const char *account, 
		const void *msg, 
		int len);

MACLIAPI int MACLI_STDCALL AxE_GetAccountState(const char *account);

MACLIAPI int MACLI_STDCALL AxE_GetAccountCount();

MACLIAPI int MACLI_STDCALL AxE_GetAccountByIndex(int index, char *account, int *type);

MACLIAPI int MACLI_STDCALL AxE_Close(const char *account);

MACLIAPI void MACLI_STDCALL AxE_Release();
#ifdef __cplusplus
}
#endif