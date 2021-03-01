#include "ss_classes.h"

namespace BeltBuckleInterface
{
	string BbPacket::GetString()
	{
		CalcCSUM();
		return kStartPacket + m_command.m_string + m_payload + m_CSUM + kEndPacket;
	}

	void BbPacket::CalcCSUM()
	{
		// TODO: Actually implement checksums.
		m_CSUM = "CSUM";
	}
}	//namespace BeltBuckleInterface

// The server calls this method to retrieve output parts from the client
void ClientBase::SendPartsToServer(PartList& partList)
{
	if (m_OutputLock.try_lock())
	{
		if (!m_OutputBuffer.empty())
		{
			for (auto& part : m_OutputBuffer)
			{
				// This should automagically overwrite any part in the list with new contents, or add new parts.
				partList[part.first] = std::move(part.second);
			}
			m_OutputBuffer.clear();
		}
	m_OutputLock.unlock();
	}
}

// The server call this method to send parts to this client
void ClientBase::SendPartsToClient(Parts::PartInstance& part)
{
	if (m_InputLock.try_lock())
	{
		m_InputBuffer[part.m_PUID] = part;
		m_InputLock.unlock();
	}
}

// The client calls this method to retrieve parts from the Input buffer, which were sent from the server.
Parts::PartInstance ClientBase::GetPartFromInputBuffer()
{
	// We want this to block because if we cannot lock the input buffer, there's no point in carrying on.
	m_InputLock.lock();
	Parts::PartInstance part = m_InputBuffer.begin()->second;
	m_InputLock.unlock();
	return std::move(part);
}

// The client calls this method to place parts in the output buffer, for retrieval by the server.
void ClientBase::PutPartInOutputBuffer(Parts::PartInstance& part) 
{
	m_OutputLock.lock();
	m_OutputBuffer.insert(std::make_pair(part.m_PUID, std::move(part)));
	m_OutputLock.unlock();
}

void ClientBase::CopyServerPartListToClient(PartList& partList)
{
	if (m_InputLock.try_lock())
	{
		m_InputBuffer = partList;
		m_InputLock.unlock();
	}
}
