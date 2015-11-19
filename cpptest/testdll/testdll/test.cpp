#include "test.h"
#include <Windows.h>


//MACLIAPI int MACLI_STDCALL add( int x, int y )
//{
//	return x+y;
//}
//
//MACLIAPI int MACLI_STDCALL sub( int x, int y )
//{
//	return x-y;
//}

MACLIAPI int MACLI_STDCALL AxE_Init( void* parentHwnd, int notifyMsg, Fun_OnMsgPtr funPtr, void *callBackParam )
{
	gCallBackFunPtr = funPtr;
	gCallBackParam = callBackParam;

	m_module = NULL;
	m_module = ::LoadLibrary(L"./GxTs.dll");
	m_fInit					= (Fun_Init)GetProcAddress(m_module, "AxE_Init");
	m_fNewMultiLogin		= (Fun_NewMultiLogin)GetProcAddress(m_module, "AxE_NewMultiLogin");
	m_fSendMsg				= (Fun_SendMsg)GetProcAddress(m_module, "AxE_SendMsg");
	m_fGetAccountState		= (Fun_GetAccountState)GetProcAddress(m_module, "AxE_GetAccountState");
	m_fGetAccountCount		= (Fun_GetAccountCount)GetProcAddress(m_module, "AxE_GetAccountCount");
	m_fGetAccountByIndex	= (Fun_GetAccountByIndex)GetProcAddress(m_module, "AxE_GetAccountByIndex");
	m_fClose				= (Fun_Close)GetProcAddress(m_module, "AxE_Close");
	m_fRelease				= (Fun_Release)GetProcAddress(m_module, "AxE_Release");

	return m_fInit(parentHwnd, notifyMsg, funPtr, callBackParam);
}

MACLIAPI int MACLI_STDCALL AxE_NewMultiLogin( NewLoginInfo *infos )
{
	return m_fNewMultiLogin(infos);
}

MACLIAPI int MACLI_STDCALL AxE_SendMsg( const char *account, const void *msg, int len )
{
	//Sleep(100);
	//char szMsgSend[1024] = {0};
	//memcpy(szMsgSend, msg, len);
	//printf("TestDll revc the msg is:%s\n", szMsgSend);
	//char szMsg[] = "callback msg";
	//gCallBackFunPtr(szMsg, sizeof(szMsg), "1231212", gCallBackParam);
	//return 0;

	return m_fSendMsg(account, msg, len);
}

MACLIAPI int MACLI_STDCALL AxE_GetAccountState(const char *account)
{
	return m_fGetAccountState(account);
}

MACLIAPI int MACLI_STDCALL AxE_GetAccountByIndex(int index, char *account, int *type)
{
	return m_fGetAccountByIndex(index, account, type);
}

MACLIAPI int MACLI_STDCALL AxE_Close(const char *account)
{
	return m_fClose(account);
}

MACLIAPI void MACLI_STDCALL AxE_Release()
{
	return m_fRelease();
}

MACLIAPI int MACLI_STDCALL AxE_GetAccountCount()
{
	return m_fGetAccountCount();
}

